import { useEffect, useRef } from "react";
import type { GameState } from "../game/types";
import { computeTransform, renderGame, screenToWorld } from "../game/render";
import { throwDrink } from "../game/engine";
import { useGameLoop } from "../hooks/useGameLoop";

interface Props {
  state: GameState;
  onStep: () => void;
  onTick: () => void;
}

export function GameCanvas({ state, onStep, onTick }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const dprRef = useRef<number>(1);

  // Handle resizing / DPR
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const handleResize = () => {
      const rect = canvas.getBoundingClientRect();
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      dprRef.current = dpr;
      canvas.width = Math.max(1, Math.floor(rect.width * dpr));
      canvas.height = Math.max(1, Math.floor(rect.height * dpr));
    };
    handleResize();
    const ro = new ResizeObserver(handleResize);
    ro.observe(canvas);
    window.addEventListener("orientationchange", handleResize);
    return () => {
      ro.disconnect();
      window.removeEventListener("orientationchange", handleResize);
    };
  }, []);

  const doRender = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const dpr = dprRef.current;
    const viewW = canvas.width / dpr;
    const viewH = canvas.height / dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    const t = computeTransform(viewW, viewH, state.worldW, state.worldH);
    renderGame(ctx, state, t);
    onTick();
  };

  useGameLoop(true, onStep, doRender);

  const handlePointer = (clientX: number, clientY: number) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const dpr = dprRef.current;
    const viewW = canvas.width / dpr;
    const viewH = canvas.height / dpr;
    const sx = clientX - rect.left;
    const sy = clientY - rect.top;
    const t = computeTransform(viewW, viewH, state.worldW, state.worldH);
    const { x, y } = screenToWorld(sx, sy, t);
    throwDrink(state, x, y);
  };

  return (
    <canvas
      ref={canvasRef}
      className="canvas"
      onPointerDown={(e) => {
        if ((e.target as HTMLElement).closest(".hud") == null) {
          e.preventDefault();
          handlePointer(e.clientX, e.clientY);
        }
      }}
    />
  );
}
