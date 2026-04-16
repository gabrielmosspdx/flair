import type { DrinkType } from "./constants";

export interface Customer {
  id: number;
  x: number;
  y: number;
  vx: number;
  vy: number;
  speed: number;
  drink: DrinkType;
  size: number;
  served: boolean;
  success: boolean;
  angle: number;
  dialogue: string | null;
  dialogueTimer: number;
  exitTimer: number;
  animPhase: number;
}

export interface Projectile {
  id: number;
  x: number;
  y: number;
  vx: number;
  vy: number;
  drink: DrinkType;
  size: number;
  life: number;
  maxLife: number;
  angle: number;
}

export interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  life: number;
  maxLife: number;
  color: string;
  size: number;
}

export interface ScorePopup {
  x: number;
  y: number;
  text: string;
  color: string;
  life: number;
  maxLife: number;
}

export type SceneName = "menu" | "game" | "gameover";

export interface GameStats {
  finalScore: number;
  finalWave: number;
}

export interface GameState {
  // World
  worldW: number;
  worldH: number;
  barX: number;
  barY: number;

  // Status
  running: boolean;
  paused: boolean;
  gameOver: boolean;

  // Progression
  score: number;
  lives: number;
  wave: number;
  waveSize: number;
  customersSpawned: number;
  spawnTimer: number;
  waveTransitionTimer: number;

  // Inventory
  inventory: Record<DrinkType, number>;
  selectedDrink: DrinkType;
  isRestocking: boolean;
  restockTimer: number;

  // Entities
  customers: Customer[];
  projectiles: Projectile[];
  particles: Particle[];
  popups: ScorePopup[];

  // FX
  livesFlashTimer: number;
  scoreFlashTimer: number;
  nextId: number;
}
