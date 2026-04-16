import { DRINK_EMOJI, DRINK_TYPES, type DrinkType } from "../game/constants";

interface Props {
  score: number;
  wave: number;
  lives: number;
  inventory: Record<DrinkType, number>;
  selectedDrink: DrinkType;
  isRestocking: boolean;
  restockProgress: number;
  paused: boolean;
  livesFlashing: boolean;
  onSelect: (drink: DrinkType) => void;
  onRestock: () => void;
  onPause: () => void;
  onQuit: () => void;
}

export function HUD({
  score,
  wave,
  lives,
  inventory,
  selectedDrink,
  isRestocking,
  restockProgress,
  paused,
  livesFlashing,
  onSelect,
  onRestock,
  onPause,
  onQuit,
}: Props) {
  const hearts = "\u2665".repeat(Math.max(0, lives));
  return (
    <div className="hud">
      <div className="hud-top">
        <div className="panel stats">
          <div className="row">
            <div>
              <div className="label">SCORE</div>
              <div className="value">{score}</div>
            </div>
            <div>
              <div className="label">WAVE</div>
              <div className="value">{wave}</div>
            </div>
          </div>
          <div style={{ marginTop: 4 }}>
            <div className="label">LIVES</div>
            <div className={`hearts ${livesFlashing ? "flash" : ""}`}>
              {hearts || "-"}
            </div>
          </div>
        </div>

        <div style={{ display: "flex", gap: 8 }}>
          <button className="icon-btn" onClick={onPause} aria-label="Pause">
            {paused ? "\u25B6" : "\u2759\u2759"}
          </button>
          <button className="icon-btn" onClick={onQuit} aria-label="Quit">
            {"\u2715"}
          </button>
        </div>
      </div>

      <div className="hud-bottom">
        {DRINK_TYPES.map((d, i) => {
          const count = inventory[d];
          const selected = d === selectedDrink;
          return (
            <button
              key={d}
              className={`drink-btn ${selected ? "selected" : ""} ${
                count <= 0 ? "empty" : ""
              }`}
              disabled={count <= 0 || isRestocking}
              onClick={() => onSelect(d)}
              aria-label={`Select ${d}`}
            >
              <span className="icon">{DRINK_EMOJI[d]}</span>
              <span className="count">{count}</span>
              <span style={{ fontSize: 10, opacity: 0.6 }}>{i + 1}</span>
            </button>
          );
        })}
        <button
          className="restock-btn"
          onClick={onRestock}
          disabled={isRestocking}
          aria-label="Restock"
        >
          <span className="icon">{"\u21BB"}</span>
          <span>RESTOCK</span>
        </button>
      </div>

      {isRestocking && (
        <div className="overlay">
          <h2 className="title" style={{ fontSize: "clamp(32px,8vw,64px)" }}>
            Restocking…
          </h2>
          <div className="progress">
            <div style={{ width: `${Math.round(restockProgress * 100)}%` }} />
          </div>
        </div>
      )}

      {paused && !isRestocking && (
        <div className="overlay">
          <h2 className="title">Paused</h2>
          <button className="btn primary" onClick={onPause}>
            Resume
          </button>
          <button className="btn ghost" onClick={onQuit}>
            Main Menu
          </button>
        </div>
      )}
    </div>
  );
}
