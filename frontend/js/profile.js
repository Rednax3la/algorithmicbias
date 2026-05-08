// ============================================================
// Profile Form Logic
// ============================================================

const URBAN_COUNTIES = ['Nairobi', 'Mombasa', 'Kisumu', 'Nakuru', 'Eldoret']
let selectedDevice = null
let currentStep = 1

// ── Auth guard ──────────────────────────────────────────────
;(async () => {
  const { data: { session } } = await supabase.auth.getSession()
  if (!session) {
    window.location.href = 'auth.html'
    return
  }
  document.getElementById('nav-user-email').textContent = session.user.email
})()

async function signOut() {
  await supabase.auth.signOut()
  window.location.href = 'auth.html'
}

// ── Step navigation ─────────────────────────────────────────
function goToStep(step) {
  if (step > currentStep && !validateStep(currentStep)) return

  // Update panels
  document.querySelectorAll('.step-panel').forEach((p, i) => {
    p.classList.toggle('active', i + 1 === step)
  })

  // Update indicators
  for (let i = 1; i <= 3; i++) {
    const indicator = document.getElementById(`step-indicator-${i}`)
    const connector = document.getElementById(`connector-${i}`)
    if (i < step) {
      indicator.classList.remove('active')
      indicator.classList.add('done')
      indicator.querySelector('.progress-step__circle').textContent = '✓'
      if (connector) connector.classList.add('done')
    } else if (i === step) {
      indicator.classList.add('active')
      indicator.classList.remove('done')
      indicator.querySelector('.progress-step__circle').textContent = i
    } else {
      indicator.classList.remove('active', 'done')
      indicator.querySelector('.progress-step__circle').textContent = i
      if (connector) connector.classList.remove('done')
    }
  }

  currentStep = step
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function validateStep(step) {
  clearAlert()
  if (step === 1) {
    const required = ['age', 'gender', 'county', 'location_type', 'education', 'employment_status']
    for (const field of required) {
      const el = document.getElementById(field)
      if (!el.value) {
        showAlert('Please fill in all fields before continuing.')
        el.focus()
        return false
      }
    }
    const age = parseInt(document.getElementById('age').value)
    if (age < 18 || age > 65) {
      showAlert('Age must be between 18 and 65.')
      return false
    }
  }
  if (step === 3) {
    if (!selectedDevice) {
      document.getElementById('device-error').classList.remove('hidden')
      return false
    }
  }
  return true
}

// ── County → Location type ───────────────────────────────────
function autoFillLocation() {
  const county = document.getElementById('county').value
  const locType = document.getElementById('location_type')
  if (county) {
    locType.value = URBAN_COUNTIES.includes(county) ? 'Urban' : 'Rural'
  }
}

// ── Slider display ───────────────────────────────────────────
function updateSliderDisplay(inputId, displayId, prefix = '', suffix = '', format = false) {
  const val = document.getElementById(inputId).value
  const el = document.getElementById(displayId)
  if (format) {
    el.textContent = prefix + Number(val).toLocaleString() + suffix
  } else {
    el.textContent = prefix + val + suffix
  }
}

// ── Repayment rate toggle ────────────────────────────────────
function toggleRepaymentRate() {
  const loans = parseInt(document.getElementById('previous_loans').value)
  const group = document.getElementById('repayment-rate-group')
  group.style.display = loans > 0 ? 'block' : 'none'
  if (loans === 0) {
    document.getElementById('repayment_rate').value = 0
  }
}

// ── Device selection ─────────────────────────────────────────
function selectDevice(card, value) {
  document.querySelectorAll('.device-card').forEach(c => c.classList.remove('selected'))
  card.classList.add('selected')
  selectedDevice = value
  document.getElementById('device-error').classList.add('hidden')
}

// ── Alert helpers ────────────────────────────────────────────
function showAlert(message, type = 'error') {
  const el = document.getElementById('form-alert')
  el.className = `alert alert--${type}`
  el.textContent = message
  el.classList.remove('hidden')
}

function clearAlert() {
  const el = document.getElementById('form-alert')
  el.className = 'hidden'
  el.textContent = ''
}

// ── Form submit ──────────────────────────────────────────────
document.getElementById('profile-form').addEventListener('submit', async (e) => {
  e.preventDefault()

  if (!validateStep(3)) return
  if (!selectedDevice) {
    document.getElementById('device-error').classList.remove('hidden')
    return
  }

  const btn = document.getElementById('submit-btn')
  btn.disabled = true
  btn.textContent = 'Saving and calculating...'

  try {
    const { data: { session } } = await supabase.auth.getSession()
    if (!session) { window.location.href = 'auth.html'; return }

    const userId = session.user.id
    const previousLoans = parseInt(document.getElementById('previous_loans').value)

    const profileData = {
      id: userId,
      age: parseInt(document.getElementById('age').value),
      gender: document.getElementById('gender').value,
      county: document.getElementById('county').value,
      location_type: document.getElementById('location_type').value,
      education: document.getElementById('education').value,
      employment_status: document.getElementById('employment_status').value,
      monthly_income: parseFloat(document.getElementById('monthly_income').value),
      mpesa_transactions_monthly: parseInt(document.getElementById('mpesa_transactions_monthly').value),
      avg_transaction_amount: parseFloat(document.getElementById('avg_transaction_amount').value),
      account_age_months: parseInt(document.getElementById('account_age_months').value),
      previous_loans: previousLoans,
      repayment_rate: previousLoans > 0
        ? parseFloat(document.getElementById('repayment_rate').value) / 100
        : 1.0,
      device_type: selectedDevice,
      app_usage_days: parseInt(document.getElementById('app_usage_days').value),
      platform_connections: parseInt(document.getElementById('platform_connections').value),
      data_anonymized_consent: document.getElementById('data_anonymized_consent').checked,
    }

    // Save to Supabase profiles
    const { error: profileError } = await supabase
      .from('profiles')
      .upsert(profileData, { onConflict: 'id' })

    if (profileError) throw profileError

    // Call /api/assess
    const assessResp = await fetch('/api/assess', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, ...profileData })
    })

    if (!assessResp.ok) {
      const err = await assessResp.json().catch(() => ({}))
      throw new Error(err.error || 'Assessment failed')
    }

    window.location.href = 'dashboard.html'

  } catch (err) {
    showAlert(err.message || 'Something went wrong. Please try again.')
    btn.disabled = false
    btn.textContent = 'Get My Credit Health Report →'
  }
})
