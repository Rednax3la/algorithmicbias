// ============================================================
// Dashboard — Personal Credit Health Report
// ============================================================

let historyChart = null

async function signOut() {
  await supabase.auth.signOut()
  window.location.href = 'auth.html'
}

async function refreshAssessment() {
  const { data: { session } } = await supabase.auth.getSession()
  if (!session) return

  const { data: profile } = await supabase
    .from('profiles')
    .select('*')
    .eq('id', session.user.id)
    .maybeSingle()

  if (!profile) {
    window.location.href = 'profile.html'
    return
  }

  document.getElementById('loading-overlay').classList.remove('hidden')
  document.getElementById('no-profile-alert').classList.add('hidden')

  let resp, result
  try {
    resp = await fetch('/api/assess', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: session.user.id, ...profile })
    })
  } catch (e) {
    document.getElementById('loading-overlay').classList.add('hidden')
    showApiError('Network error — could not reach /api/assess. ' + e.message)
    return
  }
  try {
    result = await resp.json()
  } catch (e) {
    document.getElementById('loading-overlay').classList.add('hidden')
    showApiError(`API returned HTTP ${resp.status} (non-JSON). The function may not be deployed yet.`)
    return
  }

  document.getElementById('loading-overlay').classList.add('hidden')

  if (!resp.ok || result.credit_score == null) {
    showApiError('Scoring API returned an error: ' + (result?.error || `HTTP ${resp.status}`))
    return
  }

  const assessment = {
    credit_score: result.credit_score,
    approval_probability: result.approval_probability,
    approved: result.approved,
    score_without_bias: result.score_breakdown?.score_without_bias ?? result.credit_score,
    income_contribution: result.score_breakdown?.income_contribution ?? 0,
    repayment_contribution: result.score_breakdown?.repayment_contribution ?? 0,
    account_age_contribution: result.score_breakdown?.account_age_contribution ?? 0,
    transaction_contribution: result.score_breakdown?.transaction_contribution ?? 0,
    location_penalty: result.score_breakdown?.location_penalty ?? 0,
    device_penalty: result.score_breakdown?.device_penalty ?? 0,
    gender_penalty: result.score_breakdown?.gender_penalty ?? 0,
    created_at: new Date().toISOString(),
  }

  const { data: history } = await supabase
    .from('assessments')
    .select('credit_score, created_at')
    .eq('user_id', session.user.id)
    .order('created_at', { ascending: false })
    .limit(20)

  renderDashboard(assessment, history?.length ? history : [assessment])
  renderProfileSection(profile, session.user.email)
}

function showApiError(msg) {
  const el = document.getElementById('no-profile-alert')
  el.innerHTML = `<div class="alert alert--warning"><span>⚠️</span><div>${msg} &nbsp;<button class="btn btn--sm btn--outline" onclick="refreshAssessment()">Retry</button></div></div>`
  el.classList.remove('hidden')
}

// ── Main load ────────────────────────────────────────────────
;(async () => {
  const { data: { session } } = await supabase.auth.getSession()
  if (!session) {
    window.location.href = 'auth.html'
    return
  }

  // Fetch latest assessment
  const { data: assessments } = await supabase
    .from('assessments')
    .select('*')
    .eq('user_id', session.user.id)
    .order('created_at', { ascending: false })
    .limit(20)

  document.getElementById('loading-overlay').classList.add('hidden')

  if (!assessments || assessments.length === 0) {
    // No assessment in DB yet — auto-calculate now if profile exists
    await refreshAssessment()
    return
  }

  const latest = assessments[0]
  renderDashboard(latest, assessments)

  // Load and render profile details
  const { data: profile } = await supabase
    .from('profiles')
    .select('*')
    .eq('id', session.user.id)
    .maybeSingle()

  if (profile) renderProfileSection(profile, session.user.email)
})()

function renderDashboard(a, history) {
  // Header timestamp
  document.getElementById('last-updated').textContent =
    new Date(a.created_at).toLocaleDateString('en-KE', { dateStyle: 'medium' })

  // Score
  const score = Math.round(a.credit_score)
  document.getElementById('score-number').textContent = score
  drawScoreGauge(score)

  const { label, cls, desc } = getScoreStatus(score)
  document.getElementById('score-status').textContent = label
  document.getElementById('score-status').className = `score-status ${cls}`
  document.getElementById('score-desc').textContent = desc

  // Approval
  const approvalPct = Math.round(a.approval_probability * 100)
  document.getElementById('approval-rate').textContent = approvalPct + '%'
  const bar = document.getElementById('approval-bar')
  bar.style.width = approvalPct + '%'
  bar.className = `progress-bar__fill ${approvalPct >= 70 ? 'progress-bar__fill--green' : approvalPct >= 45 ? 'progress-bar__fill--yellow' : 'progress-bar__fill--red'}`

  renderPlatformInfo(approvalPct)

  // Score factors
  renderFactors(a)

  // Bias comparison
  renderBiasComparison(a)

  // Recommendations
  renderRecommendations(a)

  // History chart
  renderHistoryChart(history)
}

function getScoreStatus(score) {
  if (score >= 61) return { label: 'Good', cls: 'score-status--good', desc: 'You have a strong credit profile. Keep it up!' }
  if (score >= 45) return { label: 'Fair', cls: 'score-status--fair', desc: 'Your credit is decent but there\'s room to improve.' }
  return { label: 'Poor', cls: 'score-status--poor', desc: 'Your score needs work. See the tips below to improve.' }
}

function renderPlatformInfo(pct) {
  let text, platforms
  if (pct >= 70) {
    text = 'You are likely eligible for most digital credit products.'
    platforms = ['M-Shwari', 'Tala', 'Branch', 'KCB M-Pesa']
  } else if (pct >= 55) {
    text = 'You may qualify for smaller loan amounts on select platforms.'
    platforms = ['Tala', 'Branch (smaller amounts)']
  } else if (pct >= 40) {
    text = 'Limited options — consider microfinance lenders or SACCOs.'
    platforms = ['Microfinance only']
  } else {
    text = 'Unlikely to be approved currently. Focus on improving your score first.'
    platforms = []
  }

  document.getElementById('platform-text').innerHTML = `<p class="text-small">${text}</p>`
  const tagsEl = document.getElementById('platform-tags')
  if (platforms.length) {
    tagsEl.innerHTML = platforms.map(p => `<span class="platform-tag">✓ ${p}</span>`).join('')
  } else {
    tagsEl.innerHTML = '<p class="text-small text-muted">No platforms currently</p>'
  }
}

function renderFactors(a) {
  const positiveEl = document.getElementById('positive-factors')
  const negativeEl = document.getElementById('negative-factors')

  const positives = []
  const legitimateNegatives = []
  const biasNegatives = []

  // Positive factors
  if (a.repayment_contribution > 0) {
    positives.push({ label: 'Good repayment history', pts: '+' + a.repayment_contribution.toFixed(1) })
  }
  if (a.transaction_contribution > 0) {
    positives.push({ label: 'Active M-Pesa usage', pts: '+' + a.transaction_contribution.toFixed(1) })
  }
  if (a.account_age_contribution > 0) {
    positives.push({ label: 'Account age', pts: '+' + a.account_age_contribution.toFixed(1) })
  }
  if (a.income_contribution > 0) {
    positives.push({ label: 'Income level', pts: '+' + a.income_contribution.toFixed(1) })
  }

  // Legitimate negatives
  if (a.repayment_contribution < 0) {
    legitimateNegatives.push({ label: 'Repayment history needs improvement', pts: a.repayment_contribution.toFixed(1) })
  }
  if (a.transaction_contribution < 0) {
    legitimateNegatives.push({ label: 'Lower transaction volume', pts: a.transaction_contribution.toFixed(1) })
  }
  if (a.account_age_contribution < 0) {
    legitimateNegatives.push({ label: 'Short account history', pts: a.account_age_contribution.toFixed(1) })
  }
  if (a.income_contribution < 0) {
    legitimateNegatives.push({ label: 'Income below median', pts: a.income_contribution.toFixed(1) })
  }

  // Bias factors
  if (a.location_penalty && a.location_penalty < 0) {
    biasNegatives.push({
      label: 'Rural location',
      pts: a.location_penalty.toFixed(1),
      source: 'KIPPRA 2021, FinAccess 2021'
    })
  }
  if (a.device_penalty && a.device_penalty < 0) {
    biasNegatives.push({
      label: 'Device type (used as income proxy)',
      pts: a.device_penalty.toFixed(1),
      source: 'Berg et al., 2020'
    })
  }
  if (a.gender_penalty && a.gender_penalty < 0) {
    biasNegatives.push({
      label: 'Gender',
      pts: a.gender_penalty.toFixed(1),
      source: 'Asante et al., 2025; FinAccess 2024'
    })
  }

  positiveEl.innerHTML = positives.length
    ? positives.map(f => `
        <div class="factor-item factor-item--positive">
          <span class="factor-item__icon">✓</span>
          <div class="factor-item__content">
            <span class="factor-item__title">${f.label}</span>
            <span class="factor-item__points"> (${f.pts} pts)</span>
          </div>
        </div>`).join('')
    : '<p class="text-small text-muted">No strong positive factors yet.</p>'

  const negHTML =
    (legitimateNegatives.length ? `<p class="text-small" style="font-weight:600; color:var(--text-muted); margin-bottom:0.5rem;">Legitimate risk factors</p>` +
      legitimateNegatives.map(f => `
        <div class="factor-item factor-item--legitimate">
          <span class="factor-item__icon">—</span>
          <div class="factor-item__content">
            <span class="factor-item__title">${f.label}</span>
            <span class="factor-item__points"> (${f.pts} pts)</span>
          </div>
        </div>`).join('') : '') +
    (biasNegatives.length ? `<p class="text-small" style="font-weight:600; color:var(--bias-red); margin-bottom:0.5rem; margin-top:0.75rem;">⚠️ Bias-flagged factors</p>` +
      biasNegatives.map(f => `
        <div class="factor-item factor-item--bias">
          <span class="factor-item__icon">⚠️</span>
          <div class="factor-item__content">
            <div class="factor-item__title">${f.label}
              <span class="factor-item__points"> (${f.pts} pts)</span>
            </div>
            <div class="bias-label">⚠ ALGORITHMIC BIAS</div>
            <div class="factor-item__source">Research identifies this as bias, not a reflection of creditworthiness. Source: ${f.source}</div>
          </div>
        </div>`).join('') : '')

  negativeEl.innerHTML = negHTML || '<p class="text-small text-muted">No negative factors identified.</p>'
}

function renderBiasComparison(a) {
  const actual = Math.round(a.credit_score)
  const fair = Math.round(a.score_without_bias)
  const diff = fair - actual

  document.getElementById('actual-score-label').textContent = actual
  document.getElementById('fair-score-label').textContent = fair
  document.getElementById('actual-score-bar').style.width = actual + '%'
  document.getElementById('fair-score-bar').style.width = fair + '%'

  let callout
  if (diff > 0) {
    callout = `Algorithmic bias is costing you <strong>${diff} points</strong>. ` +
      (fair >= 55 && actual < 55 ? 'Without these research-identified biases, you would likely be approved.' : `Your fair score would be ${fair}/100.`)
  } else {
    callout = `No bias penalties detected in your profile. Your score reflects your actual financial behaviour.`
  }
  document.getElementById('bias-callout-text').innerHTML = callout
}

function renderRecommendations(a) {
  const list = document.getElementById('recommendations-list')
  const recs = []

  if (a.transaction_contribution <= 0) {
    recs.push({ icon: '📲', text: 'Increase your M-Pesa activity. Aim for 30+ transactions per month to show financial engagement.' })
  }
  if (!a.repayment_contribution || a.repayment_contribution < 5) {
    recs.push({ icon: '💳', text: 'Start with a small loan (KES 500–1,000) and repay immediately to build a positive credit history.' })
  }
  if (a.account_age_contribution < 3) {
    recs.push({ icon: '📅', text: 'Continue using the platform consistently. Account age improves automatically over time.' })
  }
  if (a.income_contribution < 5) {
    recs.push({ icon: '💰', text: 'Consider documenting informal income through consistent M-Pesa deposits — this improves your income signal.' })
  }
  if (a.location_penalty && a.location_penalty < 0) {
    recs.push({ icon: '🏘️', text: `Your location is flagged as a bias factor. This is unfair — you can cite CBK guidelines if challenging a loan denial.` })
  }
  if (recs.length === 0) {
    recs.push({ icon: '🎉', text: 'Your profile is strong! Keep maintaining your good financial habits.' })
  }

  list.innerHTML = recs.map(r => `
    <div class="recommendation-item">
      <span class="recommendation-item__icon">${r.icon}</span>
      <span>${r.text}</span>
    </div>`).join('')
}

function renderHistoryChart(history) {
  const sorted = [...history].sort((a, b) => new Date(a.created_at) - new Date(b.created_at))

  document.getElementById('history-count').textContent =
    `${history.length} assessment${history.length !== 1 ? 's' : ''}`

  const ctx = document.getElementById('history-chart').getContext('2d')
  if (historyChart) historyChart.destroy()

  historyChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: sorted.map(a => new Date(a.created_at).toLocaleDateString('en-KE', { month: 'short', day: 'numeric' })),
      datasets: [{
        label: 'Credit Score',
        data: sorted.map(a => Math.round(a.credit_score)),
        borderColor: '#1a56db',
        backgroundColor: 'rgba(26,86,219,0.1)',
        tension: 0.4,
        fill: true,
        pointRadius: 5,
        pointBackgroundColor: '#1a56db',
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { min: 0, max: 100, grid: { color: '#f3f4f6' } },
        x: { grid: { display: false } }
      }
    }
  })
}

function renderProfileSection(p, email) {
  const deviceLabels = { feature_phone: 'Feature Phone', budget: 'Budget Smartphone', mid: 'Mid-Range Smartphone', high_end: 'High-End Smartphone' }
  const fields = [
    { label: 'Email',        value: email },
    { label: 'Age',          value: p.age ? `${p.age} years` : '—' },
    { label: 'Gender',       value: p.gender === 'M' ? 'Male' : p.gender === 'F' ? 'Female' : p.gender || '—' },
    { label: 'County',       value: p.county || '—' },
    { label: 'Location',     value: p.location_type || '—' },
    { label: 'Education',    value: p.education || '—' },
    { label: 'Employment',   value: p.employment_status || '—' },
    { label: 'Monthly Income', value: p.monthly_income ? `KES ${Number(p.monthly_income).toLocaleString()}` : '—' },
    { label: 'M-Pesa Tx/month', value: p.mpesa_transactions_monthly ? `${p.mpesa_transactions_monthly} transactions` : '—' },
    { label: 'Account Age',  value: p.account_age_months ? `${p.account_age_months} months` : '—' },
    { label: 'Previous Loans', value: p.previous_loans != null ? p.previous_loans : '—' },
    { label: 'Repayment Rate', value: p.repayment_rate != null && p.previous_loans > 0 ? `${Math.round(p.repayment_rate * 100)}%` : 'N/A' },
    { label: 'Device',       value: deviceLabels[p.device_type] || p.device_type || '—' },
    { label: 'App Usage',    value: p.app_usage_days != null ? `${p.app_usage_days} days/month` : '—' },
  ]

  document.getElementById('profile-details').innerHTML = fields.map(f => `
    <div style="background:var(--bg);border-radius:var(--radius);padding:0.875rem;">
      <div style="font-size:0.72rem;font-weight:600;text-transform:uppercase;letter-spacing:0.06em;color:var(--text-3);margin-bottom:0.25rem;">${f.label}</div>
      <div style="font-size:0.9rem;font-weight:600;color:var(--text);">${f.value}</div>
    </div>`).join('')
}

function drawScoreGauge(score) {
  const canvas = document.getElementById('score-gauge')
  const ctx = canvas.getContext('2d')
  const cx = 90, cy = 90, r = 72
  const startAngle = Math.PI * 0.75
  const endAngle = Math.PI * 2.25
  const scoreAngle = startAngle + (score / 100) * (endAngle - startAngle)

  // Color gradient based on score
  const color = score >= 61 ? '#057a55' : score >= 45 ? '#c27803' : '#c81e1e'

  ctx.clearRect(0, 0, 180, 180)

  // Background arc
  ctx.beginPath()
  ctx.arc(cx, cy, r, startAngle, endAngle)
  ctx.strokeStyle = '#e5e7eb'
  ctx.lineWidth = 14
  ctx.lineCap = 'round'
  ctx.stroke()

  // Score arc
  ctx.beginPath()
  ctx.arc(cx, cy, r, startAngle, scoreAngle)
  ctx.strokeStyle = color
  ctx.lineWidth = 14
  ctx.lineCap = 'round'
  ctx.stroke()

  // Number color
  document.getElementById('score-number').style.color = color
}
