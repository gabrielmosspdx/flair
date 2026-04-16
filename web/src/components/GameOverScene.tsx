
interface Props {
  score: number;
  wave: number;
  highScores: number[];
  onRestart: () => void;
  onMenu: () => void;
}

export function GameOverScene({
  score,
  wave,
  highScores,
  onRestart,
  onMenu,
}: Props) {
  return (
    <div className="scene">
      <h1 className="menu-title" style={{ color: "#e63c3c" }}>
        Last Call!
      </h1>

      <div className="stats-grid">
        <div className="k">DRINKS SERVED</div>
        <div className="v">{score}</div>
        <div className="k">LAST WAVE</div>
        <div className="v">{wave}</div>
      </div>

      {highScores.length > 0 && (
        <div className="high-scores">
          <h3>TOP SCORES</h3>
          <ol>
            {highScores.slice(0, 5).map((s, i) => (
              <li key={i}>
                <span>#{i + 1}</span>
                <span>{s}</span>
              </li>
            ))}
          </ol>
        </div>
      )}

      <button className="btn primary" onClick={onRestart}>
        Play Again
      </button>
      <button className="btn ghost" onClick={onMenu}>
        Main Menu
      </button>
    </div>
  );
}
