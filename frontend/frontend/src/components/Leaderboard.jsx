import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import axios from 'axios'

const API_BASE_URL = 'http://127.0.0.1:5000/api'

const Leaderboard = () => {
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [lastUpdated, setLastUpdated] = useState(null)
  const isMountedRef = useRef(true)

  const loadLeaderboard = useCallback(async () => {
    if (isMountedRef.current) {
      setLoading(true)
      setError('')
    }

    try {
      const response = await axios.get(`${API_BASE_URL}/leaderboard`)
      const payload = response.data
      const leaderboard = Array.isArray(payload?.data) ? payload.data : []
      if (!isMountedRef.current) return
      setRows(leaderboard)
      setLastUpdated(new Date())
    } catch (err) {
      if (!isMountedRef.current) return
      setError('Unable to load leaderboard')
      setRows([])
    } finally {
      if (isMountedRef.current) {
        setLoading(false)
      }
    }
  }, [])

  useEffect(() => {
    isMountedRef.current = true

    const loadWithGuard = async () => {
      await loadLeaderboard()
    }

    loadWithGuard()
    const intervalId = setInterval(loadWithGuard, 10000)

    return () => {
      isMountedRef.current = false
      clearInterval(intervalId)
    }
  }, [loadLeaderboard])

  const displayRows = useMemo(() => {
    return rows.map((row) => ({
      ...row,
      savedDate: new Date(row.saved_at).toLocaleDateString(),
    }))
  }, [rows])

  if (loading) {
    return <div className="state-card loading">Loading leaderboard...</div>
  }

  if (error) {
    return <div className="state-card error">{error}</div>
  }

  if (rows.length === 0) {
    return <div className="state-card">No leaderboard data available</div>
  }

  return (
    <div className="leaderboard">
      <div className="leaderboard-title">
        <div>
          <h2>Leaderboard</h2>
          <p className="muted">
            {lastUpdated
              ? `Last updated ${lastUpdated.toLocaleTimeString()}`
              : 'Fetching latest scores'}
          </p>
        </div>
        <button className="refresh" onClick={loadLeaderboard} type="button">
          Refresh
        </button>
      </div>
      <div className="leaderboard-header">
        <span>Rank</span>
        <span>Player</span>
        <span>Game</span>
        <span>Score</span>
        <span>Date</span>
      </div>
      {displayRows.map((row) => (
        <div
          key={`${row.player_id}-${row.rank}`}
          className={`leaderboard-row rank-${row.rank}`}
        >
          <span>#{row.rank}</span>
          <span>{row.display_name}</span>
          <span>{row.game_name}</span>
          <span>{row.highest_score}</span>
          <span>{row.savedDate}</span>
        </div>
      ))}
    </div>
  )
}

export default Leaderboard
