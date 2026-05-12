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
  el.innerHTML = message
  el.classList.remove('hidden')
}

function clearAlert() {
  const el = document.getElementById('auth-alert')
  el.className = 'hidden'
  el.innerHTML = ''
}

function setLoading(btnId, loading) {
  const btn = document.getElementById(btnId)
  btn.disabled = loading
  btn.textContent = loading
    ? (btnId === 'signin-btn' ? 'Signing in...' : 'Creating account...')
    : (btnId === 'signin-btn' ? 'Sign In' : 'Create Free Account')
}

// ── Sign In ──────────────────────────────────────────────────
async function handleSignIn(event) {
  event.preventDefault()
  clearAlert()

  const email    = document.getElementById('signin-email').value.trim()
  const password = document.getElementById('signin-password').value

  setLoading('signin-btn', true)

  try {
    const { data, error } = await supabase.auth.signInWithPassword({ email, password })
    if (error) throw error

    // Check if profile already filled out
    const { data: profile } = await supabase
      .from('profiles')
      .select('id')
      .eq('id', data.user.id)
      .maybeSingle()

    window.location.href = profile ? 'dashboard.html' : 'profile.html'
  } catch (err) {
    let msg = err.message || 'Sign in failed.'
    if (msg.toLowerCase().includes('email not confirmed')) {
      msg = 'Please verify your email first. Check your inbox for the confirmation link.'
    } else if (msg.toLowerCase().includes('invalid login')) {
      msg = 'Incorrect email or password.'
    }
    showAlert(msg)
    setLoading('signin-btn', false)
  }
}

// ── Sign Up ──────────────────────────────────────────────────
async function handleSignUp(event) {
  event.preventDefault()
  clearAlert()

  const email    = document.getElementById('signup-email').value.trim()
  const password = document.getElementById('signup-password').value
  const confirm  = document.getElementById('signup-confirm').value

  if (password !== confirm) { showAlert("Passwords don't match."); return }
  if (password.length < 8)  { showAlert('Password must be at least 8 characters.'); return }

  setLoading('signup-btn', true)

  // emailRedirectTo tells Supabase where to send the user after they
  // click the verification link — must point to the live site, not localhost.
  const redirectTo = window.location.origin + '/auth.html'

  try {
    const { error } = await supabase.auth.signUp({
      email,
      password,
      options: { emailRedirectTo: redirectTo },
    })
    if (error) throw error

    // Show confirmation message — DO NOT redirect yet.
    // The user must click the verification link first.
    // When they do, Supabase redirects back to auth.html with a token
    // in the URL hash, which the SDK processes automatically on load.
    showAlert(
      `<strong>Account created!</strong> We've sent a verification link to <strong>${email}</strong>.
       Please check your inbox (and spam folder) and click the link to activate your account.
       Then come back here to sign in.`,
      'success'
    )
    document.getElementById('signup-form').reset()
    setLoading('signup-btn', false)

  } catch (err) {
    let msg = err.message || 'Sign up failed.'
    if (msg.toLowerCase().includes('already registered')) {
      msg = 'An account with that email already exists. Try signing in.'
    }
    showAlert(msg)
    setLoading('signup-btn', false)
  }
}

// ── Sign Out ─────────────────────────────────────────────────
async function signOut() {
  await supabase.auth.signOut()
  window.location.href = 'auth.html'
}

// ── On page load ─────────────────────────────────────────────
// Handles two cases:
// 1. User is already signed in → skip auth page entirely
// 2. User clicked the verification email link → Supabase puts
//    access_token in the URL hash; the SDK processes it automatically,
//    then getSession() returns a valid session → redirect into the app
;(async () => {
  const { data: { session } } = await supabase.auth.getSession()
  if (!session) return  // not signed in, show the form normally

  // Signed in — go to profile if incomplete, otherwise dashboard
  const { data: profile } = await supabase
    .from('profiles')
    .select('id')
    .eq('id', session.user.id)
    .maybeSingle()

  window.location.href = profile ? 'dashboard.html' : 'profile.html'
})()
