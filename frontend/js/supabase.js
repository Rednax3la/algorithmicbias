// ============================================================
// Supabase Client Initialization
// The anon key is safe to expose in the frontend — RLS policies
// ensure users can only access their own data.
// ============================================================

const SUPABASE_URL = 'YOUR_SUPABASE_URL'       // Replace with your project URL
const SUPABASE_ANON_KEY = 'YOUR_SUPABASE_ANON_KEY'  // Replace with your anon/public key

const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY)
