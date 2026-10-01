import { supabase } from './supabase'

export const API_BASE = 'http://localhost:8000'

export async function registerUser({ name, email, password }) {
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
    options: { data: { name } },
  })
  if (error) throw new Error(error.message)
  return data
}

export async function loginUser({ email, password }) {
  const { data, error } = await supabase.auth.signInWithPassword({ email, password })
  if (error) throw new Error(error.message)
  return data
}

export async function loginWithGoogle() {
  const { error } = await supabase.auth.signInWithOAuth({ provider: 'google' })
  if (error) throw new Error(error.message)
}

export async function getSession() {
  const { data } = await supabase.auth.getSession()
  return data.session
}

export async function logout() {
  await supabase.auth.signOut()
}