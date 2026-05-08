// ============================================================
// Auth Logic — Sign In / Sign Up / Sign Out
// ============================================================

function switchTab(tab) {
  document.getElementById('signin-form').classList.toggle('hidden', tab !== 'signin')
  document.getElementById('signup-form').classList.toggle('hidden', tab !== 'signup')
  document.getElementById('tab-signin').classList.toggle('active', tab === 'signin')
  document.getElementById('tab-signup').classList.toggle('active', tab === 'signup')
  clearAlert()
}

function showAlert(message, type = 'error') {
  const el = document.getElementById('auth-alert')
  el.className = `alert alert--${type}`
  el.textContent = message
  el.classList.remove('hidden')
}

function clearAlert() {
  const el = document.getElementById('auth-alert')
  el.className = 'hidden'
  el.textContent = ''
}

function setLoading(btnId, loading) {
  const btn = document.getElementById(btnId)
  btn.disabled = loading
  btn.textContent = loading
    ? (btnId === 'signin-btn' ? 'Signing in...' : 'Creating account...')
    : (btnId === 'signin-btn' ? 'Sign In' : 'Create Free Account')
}

async function handleSignIn(event) {
  event.preventDefault()
  clearAlert()

  const email = document.getElementById('signin-email').value.trim()
  const password = document.getElementById('signin-password').value

  setLoading('signin-btn', true)

  try {
    const { data, error } = await supabase.auth.signInWithPassword({ email, password })
    if (error) throw error

    // Check if profile exists
    const { data: profile } = await supabase
      .from('profiles')
      .select('id')
      .eq('id', data.user.id)
      .maybeSingle()

    if (profile) {
      window.location.href = 'dashboard.html'
    } else {
      window.location.href = 'profile.html'
    }
  } catch (err) {
    showAlert(err.message || 'Sign in failed. Please check your credentials.')
    setLoading('signin-btn', false)
  }
}

async function handleSignUp(event) {
  event.preventDefault()
  clearAlert()

  const email = document.getElementById('signup-email').value.trim()
  const password = document.getElementById('signup-password').value
  const confirm = document.getElementById('signup-confirm').value

  if (password !== confirm) {
    showAlert("Passwords don't match.")
    return
  }
  if (password.length < 8) {
    showAlert('Password must be at least 8 characters.')
    return
  }

  setLoading('signup-btn', true)

  try {
    const { error } = await supabase.auth.signUp({ email, password })
    if (error) throw error

    showAlert('Account created! Redirecting to your profile...', 'success')
    setTimeout(() => { window.location.href = 'profile.html' }, 1500)
  } catch (err) {
    showAlert(err.message || 'Sign up failed. Please try again.')
    setLoading('signup-btn', false)
  }
}

async function signOut() {
  await supabase.auth.signOut()
  window.location.href = 'auth.html'
}

// On page load: if already signed in, redirect appropriately
;(async () => {
  const { data: { session } } = await supabase.auth.getSession()
  if (session) {
    const { data: profile } = await supabase
      .from('profiles')
      .select('id')
      .eq('id', session.user.id)
      .maybeSingle()

    window.location.href = profile ? 'dashboard.html' : 'profile.html'
  }
})()
