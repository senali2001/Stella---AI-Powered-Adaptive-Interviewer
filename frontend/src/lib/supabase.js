import { createClient } from '@supabase/supabase-js'

const SUPABASE_URL = 'https://cckykztcqqewcafivsyz.supabase.co'
const SUPABASE_ANON_KEY = 'sb_publishable_efqGZX7Re6_HMo_yKi19Jw_NS8KmU-B'

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)