// ============================================================
// nav.js — Auth-aware navigation for public pages
// Included on index.html and research.html.
// Checks session and swaps nav links/bottom-nav for logged-in users.
// ============================================================

;(async () => {
  // supabase client is initialised in supabase.js which must load first
  if (typeof supabase === 'undefined') return

  const { data: { session } } = await supabase.auth.getSession()

  if (!session) return  // guest — leave the default public nav as-is

  // ── Desktop nav ────────────────────────────────────────────
  const navLinks = document.querySelector('.nav__links')
  if (navLinks) {
    navLinks.innerHTML = `
      <a href="dashboard.html" class="nav__link">My Dashboard</a>
      <a href="research.html"  class="nav__link">Research</a>
      <a href="profile.html"   class="nav__link">Edit Profile</a>
      <button onclick="handleSignOut()" class="btn btn--ghost btn--sm">Sign Out</button>
    `
  }

  // ── Mobile slide-down menu ──────────────────────────────────
  const mobileMenu = document.getElementById('mobile-menu')
  if (mobileMenu) {
    mobileMenu.innerHTML = `
      <a href="dashboard.html">My Dashboard</a>
      <a href="research.html">Research</a>
      <a href="profile.html">Edit Profile</a>
      <button onclick="handleSignOut()" style="background:none;border:none;font-size:1rem;font-weight:500;color:var(--red);text-align:left;padding:0.5rem 0;cursor:pointer;">Sign Out</button>
    `
  }

  // ── Mobile bottom nav ───────────────────────────────────────
  // Replace the "Sign In" tab with "Dashboard"
  const authTab = document.getElementById('nav-auth-tab')
  if (authTab) {
    authTab.href = 'dashboard.html'
    authTab.innerHTML = `<span class="mobile-bottom-nav__icon">📈</span> Dashboard`
    authTab.classList.remove('active')
  }
})()

async function handleSignOut() {
  await supabase.auth.signOut()
  window.location.href = 'auth.html'
}
