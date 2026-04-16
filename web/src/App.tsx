import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { MenuScene } from "./components/MenuScene";
import { GameOverScene } from "./components/GameOverScene";
import { GameCanvas } from "./components/GameCanvas";
import { HUD } from "./components/HUD";
import {
  createInitialState,
  selectDrink,
  startRestock,
  togglePause,
  updateGame,
} from "./game/engine";
import { RESTOCK_DURATION, type DrinkType } from "./game/constants";
import type { GameState, SceneName } from "./game/types";

const HIGH_SCORES_KEY = "flair-web-highscores-v1";

function loadHighScores(): number[] {
  try {
    const raw = localStorage.getItem(HIGH_SCORES_KEY);
    if (!raw) return [];
    const arr = JSON.parse(raw);
    if (Array.isArray(arr)) return arr.filter((n) => typeof n === "number");
  } catch {
    /* ignore */
  }
  return [];
}

function saveHighScore(score: number): number[] {
  const scores = loadHighScores();
  scores.push(score);
  scores.sort((a, b) => b - a);
  const top = scores.slice(0, 5);
  try {
    localStorage.setItem(HIGH_SCORES_KEY, JSON.stringify(top));
  } catch {
    /* ignore */
  }
  return top;
}

interface HudSnapshot {
  score: number;
  wave: number;
  lives: number;
  inventory: Record<DrinkType, number>;
  selectedDrink: DrinkType;
  isRestocking: boolean;
  restockProgress: number;
  paused: boolean;
  livesFlashing: boolean;
  gameOver: boolean;
  finalScore: number;
  finalWave: number;
}

function snapshot(state: GameState): HudSnapshot {
  return {
    score: state.score,
    wave: state.wave,
    lives: state.lives,
    inventory: { ...state.inventory },
    selectedDrink: state.selectedDrink,
    isRestocking: state.isRestocking,
    restockProgress: state.isRestocking
      ? 1 - state.restockTimer / RESTOCK_DURATION
      : 0,
    paused: state.paused,
    livesFlashing: state.livesFlashTimer > 0,
    gameOver: state.gameOver,
    finalScore: state.score,
    finalWave: state.wave,
  };
}

export default function App() {
  const [scene, setScene] = useState<SceneName>("menu");
  const stateRef = useRef<GameState>(createInitialState());
  const [hud, setHud] = useState<HudSnapshot>(() => snapshot(stateRef.current));
  const [highScores, setHighScores] = useState<number[]>(() => loadHighScores());
  const gameOverRecordedRef = useRef(false);

  const handleStep = useCallback(() => {
    updateGame(stateRef.current);
  }, []);

  const handleTick = useCallback(() => {
    const s = stateRef.current;
    const livesFlashing = s.livesFlashTimer > 0;
    const restockProgress = s.isRestocking
      ? 1 - s.restockTimer / RESTOCK_DURATION
      : 0;
    setHud((prev) => {
      const changed =
        prev.score !== s.score ||
        prev.wave !== s.wave ||
        prev.lives !== s.lives ||
        prev.selectedDrink !== s.selectedDrink ||
        prev.paused !== s.paused ||
        prev.gameOver !== s.gameOver ||
        prev.isRestocking !== s.isRestocking ||
        prev.inventory.beer !== s.inventory.beer ||
        prev.inventory.wine !== s.inventory.wine ||
        prev.inventory.cocktail !== s.inventory.cocktail ||
        prev.livesFlashing !== livesFlashing ||
        (s.isRestocking &&
          Math.abs(prev.restockProgress - restockProgress) > 0.02);
      return changed ? snapshot(s) : prev;
    });

    if (s.gameOver && !gameOverRecordedRef.current) {
      gameOverRecordedRef.current = true;
      const top = saveHighScore(s.score);
      setHighScores(top);
      setScene("gameover");
    }
  }, []);

  const startGame = useCallback(() => {
    stateRef.current = createInitialState();
    gameOverRecordedRef.current = false;
    setHud(snapshot(stateRef.current));
    setScene("game");
  }, []);

  const quitToMenu = useCallback(() => {
    setScene("menu");
  }, []);

  const onSelect = useCallback((d: DrinkType) => {
    selectDrink(stateRef.current, d);
  }, []);
  const onRestock = useCallback(() => {
    startRestock(stateRef.current);
  }, []);
  const onPause = useCallback(() => {
    togglePause(stateRef.current);
  }, []);

  // Keyboard shortcuts for desktop
  useEffect(() => {
    if (scene !== "game") return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === "1") onSelect("beer");
      else if (e.key === "2") onSelect("wine");
      else if (e.key === "3") onSelect("cocktail");
      else if (e.key === "r" || e.key === "R") onRestock();
      else if (e.key === "p" || e.key === "P") onPause();
      else if (e.key === "Escape") {
        if (stateRef.current.paused) quitToMenu();
        else onPause();
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [scene, onSelect, onRestock, onPause, quitToMenu]);

  // Prevent accidental pull-to-refresh and zoom
  useEffect(() => {
    const prevent = (e: TouchEvent) => {
      if (e.touches.length > 1) e.preventDefault();
    };
    document.addEventListener("touchmove", prevent, { passive: false });
    return () => document.removeEventListener("touchmove", prevent);
  }, []);

  const topHigh = useMemo(() => highScores[0] ?? 0, [highScores]);

  return (
    <div className="app">
      {scene === "menu" && (
        <MenuScene onStart={startGame} highScore={topHigh} />
      )}

      {scene === "game" && (
        <div className="game-root">
          <GameCanvas
            state={stateRef.current}
            onStep={handleStep}
            onTick={handleTick}
          />
          <HUD
            score={hud.score}
            wave={hud.wave}
            lives={hud.lives}
            inventory={hud.inventory}
            selectedDrink={hud.selectedDrink}
            isRestocking={hud.isRestocking}
            restockProgress={hud.restockProgress}
            paused={hud.paused}
            livesFlashing={hud.livesFlashing}
            onSelect={onSelect}
            onRestock={onRestock}
            onPause={onPause}
            onQuit={quitToMenu}
          />
        </div>
      )}

      {scene === "gameover" && (
        <GameOverScene
          score={hud.finalScore}
          wave={hud.finalWave}
          highScores={highScores}
          onRestart={startGame}
          onMenu={quitToMenu}
        />
      )}
    </div>
  );
}
