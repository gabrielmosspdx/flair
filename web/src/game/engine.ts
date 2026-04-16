import {
  BASE_CUSTOMER_SPEED,
  BASE_POINTS,
  BASE_SPAWN_DELAY,
  CUSTOMER_REACH_THRESHOLD,
  CUSTOMER_SIZE,
  DIALOGUE_FRAMES,
  DRINK_COLORS,
  DRINK_TYPES,
  INITIAL_INVENTORY,
  INITIAL_LIVES,
  INITIAL_WAVE_SIZE,
  MAX_WAVE_SIZE,
  MIN_SPAWN_DELAY,
  MIN_SPAWN_DISTANCE,
  NEGATIVE_LINES,
  PARTICLE_BURST,
  PARTICLE_LIFE,
  POINTS_PER_WAVE,
  POSITIVE_LINES,
  PROJECTILE_MAX_LIFE,
  PROJECTILE_SIZE,
  PROJECTILE_SPEED,
  RESTOCK_AMOUNT,
  RESTOCK_DURATION,
  SPAWN_DELAY_REDUCTION,
  WAVE_SIZE_STEP,
  WAVE_SPEED_MULTIPLIER,
  WAVE_TRANSITION_FRAMES,
  WORLD_H,
  WORLD_W,
  type DrinkType,
} from "./constants";
import type {
  Customer,
  GameState,
  Particle,
  Projectile,
  ScorePopup,
} from "./types";

const randRange = (min: number, max: number) => Math.random() * (max - min) + min;
const randChoice = <T>(items: readonly T[]): T =>
  items[Math.floor(Math.random() * items.length)];

export function createInitialState(): GameState {
  return {
    worldW: WORLD_W,
    worldH: WORLD_H,
    barX: WORLD_W / 2,
    barY: WORLD_H / 2,

    running: true,
    paused: false,
    gameOver: false,

    score: 0,
    lives: INITIAL_LIVES,
    wave: 1,
    waveSize: INITIAL_WAVE_SIZE,
    customersSpawned: 0,
    spawnTimer: 0,
    waveTransitionTimer: WAVE_TRANSITION_FRAMES,

    inventory: {
      beer: INITIAL_INVENTORY,
      wine: INITIAL_INVENTORY,
      cocktail: INITIAL_INVENTORY,
    },
    selectedDrink: "beer",
    isRestocking: false,
    restockTimer: 0,

    customers: [],
    projectiles: [],
    particles: [],
    popups: [],

    livesFlashTimer: 0,
    scoreFlashTimer: 0,
    nextId: 1,
  };
}

function currentSpawnDelay(wave: number): number {
  return Math.max(
    MIN_SPAWN_DELAY,
    BASE_SPAWN_DELAY - (wave - 1) * SPAWN_DELAY_REDUCTION,
  );
}

function customerSpeed(wave: number): number {
  return BASE_CUSTOMER_SPEED * Math.pow(WAVE_SPEED_MULTIPLIER, wave - 1);
}

function pointsPerKill(wave: number): number {
  return BASE_POINTS + (wave - 1) * POINTS_PER_WAVE;
}

function waveSizeFor(wave: number): number {
  return Math.min(INITIAL_WAVE_SIZE + (wave - 1) * WAVE_SIZE_STEP, MAX_WAVE_SIZE);
}

function pickSpawnPosition(state: GameState): { x: number; y: number } {
  const margin = 30;
  for (let attempt = 0; attempt < 20; attempt++) {
    const edge = Math.floor(Math.random() * 4);
    let x = 0;
    let y = 0;
    if (edge === 0) {
      x = -margin;
      y = randRange(margin, state.worldH - margin);
    } else if (edge === 1) {
      x = state.worldW + margin;
      y = randRange(margin, state.worldH - margin);
    } else if (edge === 2) {
      x = randRange(margin, state.worldW - margin);
      y = -margin;
    } else {
      x = randRange(margin, state.worldW - margin);
      y = state.worldH + margin;
    }
    const tooClose = state.customers.some((c) => {
      const dx = c.x - x;
      const dy = c.y - y;
      return dx * dx + dy * dy < MIN_SPAWN_DISTANCE * MIN_SPAWN_DISTANCE;
    });
    if (!tooClose) return { x, y };
  }
  const edge = Math.floor(Math.random() * 4);
  if (edge === 0) return { x: -margin, y: state.worldH / 2 };
  if (edge === 1) return { x: state.worldW + margin, y: state.worldH / 2 };
  if (edge === 2) return { x: state.worldW / 2, y: -margin };
  return { x: state.worldW / 2, y: state.worldH + margin };
}

function spawnCustomer(state: GameState) {
  const { x, y } = pickSpawnPosition(state);
  const speed = customerSpeed(state.wave);
  const dx = state.barX - x;
  const dy = state.barY - y;
  const dist = Math.hypot(dx, dy) || 1;
  const customer: Customer = {
    id: state.nextId++,
    x,
    y,
    vx: (dx / dist) * speed,
    vy: (dy / dist) * speed,
    speed,
    drink: randChoice(DRINK_TYPES),
    size: CUSTOMER_SIZE,
    served: false,
    success: false,
    angle: Math.atan2(dy, dx),
    dialogue: null,
    dialogueTimer: 0,
    exitTimer: 0,
    animPhase: Math.random() * Math.PI * 2,
  };
  state.customers.push(customer);
  state.customersSpawned += 1;
}

function spawnBurst(state: GameState, x: number, y: number, color: string, count = PARTICLE_BURST) {
  for (let i = 0; i < count; i++) {
    const angle = Math.random() * Math.PI * 2;
    const speed = randRange(1.5, 4.5);
    const p: Particle = {
      x,
      y,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed,
      life: PARTICLE_LIFE,
      maxLife: PARTICLE_LIFE,
      color,
      size: randRange(2, 5),
    };
    state.particles.push(p);
  }
}

function addPopup(state: GameState, text: string, color: string) {
  const popup: ScorePopup = {
    x: 120,
    y: 90,
    text,
    color,
    life: 60,
    maxLife: 60,
  };
  state.popups.push(popup);
}

export function selectDrink(state: GameState, drink: DrinkType) {
  if (state.isRestocking) return;
  state.selectedDrink = drink;
}

export function startRestock(state: GameState) {
  if (state.isRestocking || state.paused || state.gameOver) return;
  state.isRestocking = true;
  state.restockTimer = RESTOCK_DURATION;
}

export function togglePause(state: GameState) {
  if (state.gameOver || state.isRestocking) return;
  state.paused = !state.paused;
}

export function throwDrink(state: GameState, targetX: number, targetY: number) {
  if (state.paused || state.gameOver || state.isRestocking) return;
  const drink = state.selectedDrink;
  if (state.inventory[drink] <= 0) return;

  const dx = targetX - state.barX;
  const dy = targetY - state.barY;
  const dist = Math.hypot(dx, dy) || 1;

  const projectile: Projectile = {
    id: state.nextId++,
    x: state.barX,
    y: state.barY,
    vx: (dx / dist) * PROJECTILE_SPEED,
    vy: (dy / dist) * PROJECTILE_SPEED,
    drink,
    size: PROJECTILE_SIZE,
    life: PROJECTILE_MAX_LIFE,
    maxLife: PROJECTILE_MAX_LIFE,
    angle: 0,
  };
  state.projectiles.push(projectile);
  state.inventory[drink] -= 1;

  if (state.inventory[drink] <= 0) {
    const next = DRINK_TYPES.find((d) => state.inventory[d] > 0);
    if (next) state.selectedDrink = next;
  }
}

function handleGameOver(state: GameState) {
  state.gameOver = true;
  state.running = false;
}

export function updateGame(state: GameState): void {
  if (!state.running || state.paused || state.gameOver) return;

  // Wave transition countdown
  if (state.waveTransitionTimer > 0) {
    state.waveTransitionTimer -= 1;
  }

  // Restock
  if (state.isRestocking) {
    state.restockTimer -= 1;
    if (state.restockTimer <= 0) {
      for (const d of DRINK_TYPES) state.inventory[d] = RESTOCK_AMOUNT;
      state.isRestocking = false;
    }
    // Keep visuals moving but no spawning/collisions during restock
  } else {
    // Spawn logic
    if (state.customersSpawned < state.waveSize) {
      state.spawnTimer += 1;
      if (state.spawnTimer >= currentSpawnDelay(state.wave)) {
        spawnCustomer(state);
        state.spawnTimer = 0;
      }
    }
  }

  // Update customers
  for (const c of state.customers) {
    if (!c.served) {
      c.x += c.vx;
      c.y += c.vy;
      c.angle = Math.atan2(state.barY - c.y, state.barX - c.x);
    } else {
      c.exitTimer -= 1;
    }
    if (c.dialogueTimer > 0) c.dialogueTimer -= 1;
    c.animPhase += 0.12;
  }

  // Update projectiles
  for (const p of state.projectiles) {
    p.x += p.vx;
    p.y += p.vy;
    p.life -= 1;
    p.angle += Math.PI / 18;
  }
  state.projectiles = state.projectiles.filter(
    (p) =>
      p.life > 0 &&
      p.x > -40 &&
      p.x < state.worldW + 40 &&
      p.y > -40 &&
      p.y < state.worldH + 40,
  );

  // Update particles
  for (const p of state.particles) {
    p.x += p.vx;
    p.y += p.vy;
    p.vx *= 0.95;
    p.vy *= 0.95;
    p.life -= 1;
  }
  state.particles = state.particles.filter((p) => p.life > 0);

  // Update popups
  for (const p of state.popups) p.life -= 1;
  state.popups = state.popups.filter((p) => p.life > 0);

  if (state.livesFlashTimer > 0) state.livesFlashTimer -= 1;
  if (state.scoreFlashTimer > 0) state.scoreFlashTimer -= 1;

  // Collisions (projectiles vs customers)
  if (!state.isRestocking) {
    for (const proj of state.projectiles) {
      if (proj.life <= 0) continue;
      for (const cust of state.customers) {
        if (cust.served) continue;
        const dx = proj.x - cust.x;
        const dy = proj.y - cust.y;
        const r = proj.size + cust.size;
        if (dx * dx + dy * dy <= r * r) {
          if (proj.drink === cust.drink) {
            const gain = pointsPerKill(state.wave);
            state.score += gain;
            cust.served = true;
            cust.success = true;
            cust.exitTimer = 45;
            cust.dialogue = randChoice(POSITIVE_LINES);
            cust.dialogueTimer = DIALOGUE_FRAMES;
            cust.vx = -cust.vx * 0.4;
            cust.vy = -cust.vy * 0.4;
            spawnBurst(state, cust.x, cust.y, DRINK_COLORS[proj.drink]);
            addPopup(state, `+${gain}`, "#50e678");
            state.scoreFlashTimer = 30;
          } else {
            state.lives -= 1;
            state.livesFlashTimer = 60;
            cust.served = true;
            cust.success = false;
            cust.exitTimer = 45;
            cust.dialogue = randChoice(NEGATIVE_LINES);
            cust.dialogueTimer = DIALOGUE_FRAMES;
            cust.vx = 0;
            cust.vy = 0;
            spawnBurst(state, cust.x, cust.y, "#e63c3c");
            addPopup(state, "-1", "#e63c3c");
            if (state.lives <= 0) handleGameOver(state);
          }
          proj.life = 0;
          break;
        }
      }
    }
  }

  // Customer reaches bar
  if (!state.isRestocking) {
    for (const c of state.customers) {
      if (c.served) continue;
      const dx = state.barX - c.x;
      const dy = state.barY - c.y;
      if (dx * dx + dy * dy < CUSTOMER_REACH_THRESHOLD * CUSTOMER_REACH_THRESHOLD) {
        state.lives -= 1;
        state.livesFlashTimer = 60;
        c.served = true;
        c.success = false;
        c.exitTimer = 1;
        spawnBurst(state, c.x, c.y, "#e63c3c", 8);
        addPopup(state, "-1", "#e63c3c");
        if (state.lives <= 0) handleGameOver(state);
      }
    }
  }

  // Remove finished customers
  state.customers = state.customers.filter(
    (c) => !(c.served && c.exitTimer <= 0),
  );

  // Wave completion
  if (
    !state.isRestocking &&
    state.customersSpawned >= state.waveSize &&
    state.customers.length === 0
  ) {
    state.wave += 1;
    state.customersSpawned = 0;
    state.waveSize = waveSizeFor(state.wave);
    state.spawnTimer = 0;
    state.waveTransitionTimer = WAVE_TRANSITION_FRAMES;
  }
}

export function resetGame(state: GameState): GameState {
  const fresh = createInitialState();
  Object.assign(state, fresh);
  return state;
}
