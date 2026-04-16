
interface Props {
  onStart: () => void;
  highScore: number;
}

export function MenuScene({ onStart, highScore }: Props) {
  return (
    <div className="scene">
      <h1 className="menu-title">Flair!</h1>
      <p className="menu-tag">throw drinks. serve chaos.</p>
      <button className="btn primary" onClick={onStart}>
        Start Game
      </button>
      {highScore > 0 && (
        <p style={{ marginTop: 20, color: "#ffaf1e", letterSpacing: 2 }}>
          HIGH SCORE: <strong style={{ color: "#fff8eb" }}>{highScore}</strong>
        </p>
      )}
      <p
        style={{
          position: "absolute",
          bottom: "calc(env(safe-area-inset-bottom) + 16px)",
          fontSize: 12,
          opacity: 0.5,
          textAlign: "center",
          padding: "0 24px",
        }}
      >
        Tap to throw drinks. Match the order above each customer's head.
        <br />
        Pick a drink below. Restock when you run out.
      </p>
    </div>
  );
}
