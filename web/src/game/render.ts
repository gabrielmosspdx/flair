import {
  BAR_SIZE,
  COLORS,
  CROSSHAIR_RADIUS,
  DRINK_COLORS,
  DRINK_EMOJI,
} from "./constants";
import type { Customer, GameState, Projectile } from "./types";

export interface ViewTransform {
  scale: number;
  offsetX: number;
  offsetY: number;
  viewW: number;
  viewH: number;
}

export function computeTransform(
  viewW: number,
  viewH: number,
  worldW: number,
  worldH: number,
): ViewTransform {
  const scale = Math.min(viewW / worldW, viewH / worldH);
  const offsetX = (viewW - worldW * scale) / 2;
  const offsetY = (viewH - worldH * scale) / 2;
  return { scale, offsetX, offsetY, viewW, viewH };
}

export function screenToWorld(
  sx: number,
  sy: number,
  t: ViewTransform,
): { x: number; y: number } {
  return {
    x: (sx - t.offsetX) / t.scale,
    y: (sy - t.offsetY) / t.scale,
  };
}

function drawFloor(ctx: CanvasRenderingContext2D, w: number, h: number) {
  const grad = ctx.createRadialGradient(w / 2, h / 2, 60, w / 2, h / 2, Math.max(w, h) / 1.4);
  grad.addColorStop(0, COLORS.bg2);
  grad.addColorStop(0.5, COLORS.bg1);
  grad.addColorStop(1, COLORS.bg0);
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, w, h);

  // Subtle plank stripes for bar atmosphere
  ctx.save();
  ctx.globalAlpha = 0.08;
  ctx.strokeStyle = "#000";
  ctx.lineWidth = 2;
  for (let y = 0; y < h; y += 70) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(w, y);
    ctx.stroke();
  }
  ctx.restore();
}

function drawBar(ctx: CanvasRenderingContext2D, x: number, y: number) {
  const s = BAR_SIZE;
  ctx.save();
  ctx.translate(x, y);

  // shadow
  ctx.fillStyle = "rgba(0,0,0,0.45)";
  ctx.fillRect(-s / 2 + 4, -s / 2 + 6, s, s);

  // Outer dark
  ctx.fillStyle = COLORS.bar;
  ctx.fillRect(-s / 2, -s / 2, s, s);

  // Inner gold
  ctx.fillStyle = COLORS.barHi;
  ctx.fillRect(-s / 2 + 6, -s / 2 + 6, s - 12, s - 12);

  // Crosshair
  ctx.strokeStyle = COLORS.gold;
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.arc(0, 0, CROSSHAIR_RADIUS, 0, Math.PI * 2);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(-CROSSHAIR_RADIUS - 4, 0);
  ctx.lineTo(-CROSSHAIR_RADIUS, 0);
  ctx.moveTo(CROSSHAIR_RADIUS, 0);
  ctx.lineTo(CROSSHAIR_RADIUS + 4, 0);
  ctx.moveTo(0, -CROSSHAIR_RADIUS - 4);
  ctx.lineTo(0, -CROSSHAIR_RADIUS);
  ctx.moveTo(0, CROSSHAIR_RADIUS);
  ctx.lineTo(0, CROSSHAIR_RADIUS + 4);
  ctx.stroke();

  ctx.restore();
}

function drawCustomer(ctx: CanvasRenderingContext2D, c: Customer) {
  ctx.save();
  ctx.translate(c.x, c.y);

  // shadow
  ctx.fillStyle = "rgba(0,0,0,0.4)";
  ctx.beginPath();
  ctx.ellipse(0, c.size + 4, c.size * 0.9, c.size * 0.35, 0, 0, Math.PI * 2);
  ctx.fill();

  const bob = Math.sin(c.animPhase) * 1.5;
  ctx.translate(0, bob);

  // body
  const bodyColor = c.served
    ? c.success
      ? "#7cc67c"
      : "#c8504c"
    : COLORS.customer;
  ctx.fillStyle = bodyColor;
  ctx.strokeStyle = "rgba(0,0,0,0.35)";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.arc(0, 0, c.size, 0, Math.PI * 2);
  ctx.fill();
  ctx.stroke();

  // face direction indicator (tiny eye)
  const ex = Math.cos(c.angle) * c.size * 0.35;
  const ey = Math.sin(c.angle) * c.size * 0.35;
  ctx.fillStyle = "#fff";
  ctx.beginPath();
  ctx.arc(ex, ey - 2, 3, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = "#111";
  ctx.beginPath();
  ctx.arc(ex + Math.cos(c.angle) * 1.5, ey - 2 + Math.sin(c.angle) * 1.5, 1.5, 0, Math.PI * 2);
  ctx.fill();

  // order bubble (drink emoji above customer)
  if (!c.served) {
    ctx.save();
    ctx.translate(0, -c.size - 18);
    ctx.fillStyle = "rgba(255,248,235,0.9)";
    ctx.strokeStyle = "rgba(0,0,0,0.3)";
    ctx.lineWidth = 1.5;
    roundRect(ctx, -18, -14, 36, 28, 8);
    ctx.fill();
    ctx.stroke();
    ctx.font = "22px serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(DRINK_EMOJI[c.drink], 0, 1);
    // pointer
    ctx.fillStyle = "rgba(255,248,235,0.9)";
    ctx.beginPath();
    ctx.moveTo(-4, 14);
    ctx.lineTo(0, 20);
    ctx.lineTo(4, 14);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
  }

  // dialogue
  if (c.dialogue && c.dialogueTimer > 0) {
    const alpha = Math.min(1, c.dialogueTimer / 40);
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.font = "bold 16px -apple-system, Helvetica, Arial, sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "bottom";
    ctx.fillStyle = c.success ? COLORS.green : COLORS.red;
    ctx.strokeStyle = "rgba(0,0,0,0.85)";
    ctx.lineWidth = 4;
    ctx.strokeText(c.dialogue, 0, -c.size - 28);
    ctx.fillText(c.dialogue, 0, -c.size - 28);
    ctx.restore();
  }

  ctx.restore();
}

function drawProjectile(ctx: CanvasRenderingContext2D, p: Projectile) {
  ctx.save();
  ctx.translate(p.x, p.y);
  ctx.rotate(p.angle);

  // trail
  ctx.strokeStyle = DRINK_COLORS[p.drink];
  ctx.lineCap = "round";
  ctx.lineWidth = 4;
  ctx.globalAlpha = 0.35;
  ctx.beginPath();
  ctx.moveTo(-p.vx * 2, -p.vy * 2);
  ctx.lineTo(0, 0);
  ctx.stroke();
  ctx.globalAlpha = 1;

  // body
  ctx.fillStyle = DRINK_COLORS[p.drink];
  ctx.strokeStyle = "rgba(0,0,0,0.5)";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.arc(0, 0, p.size, 0, Math.PI * 2);
  ctx.fill();
  ctx.stroke();

  // highlight
  ctx.fillStyle = "rgba(255,255,255,0.55)";
  ctx.beginPath();
  ctx.arc(-p.size * 0.35, -p.size * 0.35, p.size * 0.35, 0, Math.PI * 2);
  ctx.fill();

  ctx.restore();
}

function drawParticles(ctx: CanvasRenderingContext2D, state: GameState) {
  for (const p of state.particles) {
    const alpha = Math.max(0, p.life / p.maxLife);
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.fillStyle = p.color;
    ctx.beginPath();
    ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }
}

function drawWaveTransition(ctx: CanvasRenderingContext2D, state: GameState) {
  if (state.waveTransitionTimer <= 0) return;
  const t = state.waveTransitionTimer / 120;
  const alpha = Math.sin(t * Math.PI);
  const scale = 1 + (1 - t) * 0.3;

  ctx.save();
  ctx.globalAlpha = alpha;
  ctx.translate(state.worldW / 2, state.worldH / 2);
  ctx.scale(scale, scale);
  ctx.font = "bold 84px -apple-system, Helvetica, Arial, sans-serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillStyle = COLORS.gold;
  ctx.strokeStyle = "rgba(0,0,0,0.75)";
  ctx.lineWidth = 6;
  const text = `WAVE ${state.wave}`;
  ctx.strokeText(text, 0, 0);
  ctx.fillText(text, 0, 0);

  if (state.waveTransitionTimer < 60) {
    ctx.font = "bold 28px -apple-system, Helvetica, Arial, sans-serif";
    ctx.fillStyle = COLORS.white;
    ctx.strokeText("Get Ready!", 0, 60);
    ctx.fillText("Get Ready!", 0, 60);
  }
  ctx.restore();
}

function roundRect(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  w: number,
  h: number,
  r: number,
) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}

export function renderGame(
  ctx: CanvasRenderingContext2D,
  state: GameState,
  t: ViewTransform,
) {
  ctx.save();
  ctx.clearRect(0, 0, t.viewW, t.viewH);
  // Letterbox
  ctx.fillStyle = COLORS.bg0;
  ctx.fillRect(0, 0, t.viewW, t.viewH);

  ctx.translate(t.offsetX, t.offsetY);
  ctx.scale(t.scale, t.scale);

  drawFloor(ctx, state.worldW, state.worldH);
  drawBar(ctx, state.barX, state.barY);

  for (const c of state.customers) drawCustomer(ctx, c);
  for (const p of state.projectiles) drawProjectile(ctx, p);
  drawParticles(ctx, state);

  drawWaveTransition(ctx, state);

  ctx.restore();
}
