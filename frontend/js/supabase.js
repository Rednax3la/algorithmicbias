// ============================================================
// Supabase Client — vanilla JS, CDN build
// The publishable/anon key is safe in frontend code.
// RLS policies on the database enforce data isolation per user.
// ============================================================

const SUPABASE_URL     = 'https://twwblvtuluxvlbehphig.supabase.co'
const SUPABASE_ANON_KEY = 'sb_publishable_DfUXzM1yuhKH4qEFb7tKBA_WHCk8_C3'

if (typeof window.supabase === 'undefined') {
  console.error('Supabase CDN script did not load. Check the <script> tag order.')
}

const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY)
