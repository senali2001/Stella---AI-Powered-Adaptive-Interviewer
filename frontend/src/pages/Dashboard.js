import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getSession, logout, API_BASE } from '../lib/auth'

const ROLES = [
  { id: 'backend', title: 'Backend Developer', desc: 'APIs, databases, system design' },
  { id: 'frontend', title: 'Frontend Developer', desc: 'UI, React/JS, performance' },
  { id: 'fullstack', title: 'Full-Stack Developer', desc: 'End-to-end web development' },
  { id: 'qa', title: 'QA Engineer', desc: 'Testing, automation, quality' },
]

export default function Dashboard() {
  const [role, setRole] = useState(null)
  const [type, setType] = useState('Technical')
  const [starting, setStarting] = useState(false)
  const [user, setUser] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    getSession().then((session) => setUser(session?.user ?? null))
  }, [])

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const handleStart = async () => {
    if (!role) return
    setStarting(true)
    try {
      const session = await getSession()
      if (!session) {
        navigate('/login')
        return
      }

      const res = await fetch(`${API_BASE}/interview/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${session.access_token}`,
        },
        body: JSON.stringify({
          candidate_name: user?.user_metadata?.name || 'Candidate',
          role,
          interview_type: type,
        }),
      })
      const data = await res.json()
      // Next: navigate to an /interview/:sessionId page (not built yet)
      console.log('Interview started:', data)
      alert(`Interview started — session ${data.session_id}. Build the /interview page next to continue.`)
    } catch (err) {
      alert('Could not start interview — is the backend running?')
    } finally {
      setStarting(false)
    }
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div className="brand">STELLA</div>
        <h1>Hi{user?.user_metadata?.name ? `, ${user.user_metadata.name.split(' ')[0]}` : ''}</h1>
        <p>Choose a role and interview type to begin.</p>
      </div>

      <div className="section-label">Role</div>
      <div className="role-grid">
        {ROLES.map((r) => (
          <button
            key={r.id}
            className={`role-card ${role === r.id ? 'selected' : ''}`}
            onClick={() => setRole(r.id)}
            type="button"
          >
            <div className="role-title">{r.title}</div>
            <div className="role-desc">{r.desc}</div>
          </button>
        ))}
      </div>

      <div className="section-label">Interview type</div>
      <div className="type-toggle">
        {['HR', 'Technical'].map((t) => (
          <button
            key={t}
            className={type === t ? 'selected' : ''}
            onClick={() => setType(t)}
            type="button"
          >
            {t}
          </button>
        ))}
      </div>

      <button
        className="btn btn-primary start-btn"
        disabled={!role || starting}
        onClick={handleStart}
      >
        {starting ? 'Starting…' : 'Start interview'}
      </button>

      <div className="footer-link">
        <a href="#" onClick={handleLogout}>Log out</a>
      </div>
    </div>
  )
}
