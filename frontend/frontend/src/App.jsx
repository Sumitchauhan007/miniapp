import Navbar from './components/Navbar.jsx'
import Leaderboard from './components/Leaderboard.jsx'
import './App.css'

function App() {
  const games = [
    { name: 'PUBG', mode: 'Squad Ranked', accent: 'gold' },
    { name: 'COD', mode: 'Multiplayer', accent: 'silver' },
    { name: 'BGMI', mode: 'Classic', accent: 'bronze' },
    { name: 'Valorant', mode: 'Competitive', accent: 'neon' },
  ]

  return (
    <div className="app">
      <Navbar />

      <main className="main">
        <header className="hero" id="home">
          <div>
            <p className="eyebrow">Centralized game rankings</p>
            <h1>Live Leaderboards</h1>
            <p className="subtitle">
              Track top players across competitive titles in one clean dashboard.
            </p>
          </div>
          <div className="cta-card">
            <h2>Global ladder</h2>
            <p>See the best scores across all supported games.</p>
          </div>
        </header>

        <section className="games">
          <div>
            <h2 className="section-title">Featured Games</h2>
            <p className="muted">Quick view of the most active leaderboards.</p>
          </div>
          <div className="game-grid">
            {games.map((game) => (
              <article
                key={game.name}
                className={`game-card accent-${game.accent}`}
              >
                <div className="game-card-top">
                  <span className="game-tag">{game.mode}</span>
                  <span className="game-dot" aria-hidden="true"></span>
                </div>
                <h3>{game.name}</h3>
                <p className="muted">Live ranking snapshots and best runs.</p>
              </article>
            ))}
          </div>
        </section>

        <section className="panel" id="leaderboard">
          <Leaderboard />
        </section>
      </main>
    </div>
  )
}

export default App
