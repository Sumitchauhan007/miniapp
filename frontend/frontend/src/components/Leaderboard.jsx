import { useEffect, useMemo, useState } from 'react'
import axios from 'axios'

const API_BASE_URL = 'http://127.0.0.1:5000/api'

const Leaderboard = () => {
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let isActive = true

    const loadLeaderboard = async () => {
      setLoading(true)
      setError('')

      try {
        const response = await axios.get(`${API_BASE_URL}/leaderboard`)
        if (!isActive) return

        const payload = response.data
        const leaderboard = Array.isArray(payload?.data) ? payload.data : []
        setRows(leaderboard)
      } catch (err) {
        if (!isActive) return
        setError('Unable to load leaderboard')
        setRows([])
      } finally {
        if (isActive) {
          setLoading(false)
        }
      }
    }

    loadLeaderboard()

    return () => {
      isActive = false
    }
  }, [])

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
