// ============================================================
// Supabase Client Initialization
// The anon key is safe to expose in the frontend — RLS policies
// ensure users can only access their own data.
// ============================================================

const SUPABASE_URL = 'https://twwblvtuluxvlbehphig.supabase.co'       // Replace with your project URL
const SUPABASE_ANON_KEY = 'sb_publishable_DfUXzM1yuhKH4qEFb7tKBA_WHCk8_C3'  // Replace with your anon/public key

const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY)
