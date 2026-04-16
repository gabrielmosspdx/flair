export const WORLD_W = 1200;
export const WORLD_H = 800;

export const FPS = 60;
export const DT = 1000 / FPS;

export const INITIAL_LIVES = 3;
export const INITIAL_INVENTORY = 5;
export const RESTOCK_AMOUNT = 5;

export const INITIAL_WAVE_SIZE = 8;
export const MAX_WAVE_SIZE = 20;
export const WAVE_SIZE_STEP = 2;

export const BASE_SPAWN_DELAY = 120;
export const SPAWN_DELAY_REDUCTION = 8;
export const MIN_SPAWN_DELAY = 30;

export const BASE_CUSTOMER_SPEED = 0.5;
export const WAVE_SPEED_MULTIPLIER = 1.05;

export const BASE_POINTS = 10;
export const POINTS_PER_WAVE = 2;

export const PROJECTILE_SPEED = 6;
export const PROJECTILE_MAX_LIFE = 150;
export const PROJECTILE_SIZE = 10;

export const PARTICLE_LIFE = 30;
export const PARTICLE_BURST = 10;

export const RESTOCK_DURATION = 180;

export const CUSTOMER_SIZE = 22;
export const CUSTOMER_REACH_THRESHOLD = 34;
export const MIN_SPAWN_DISTANCE = 90;

export const BAR_SIZE = 60;
export const CROSSHAIR_RADIUS = 8;

export const DIALOGUE_FRAMES = 120;
export const WAVE_TRANSITION_FRAMES = 120;

export const COLORS = {
  bg0: "#1a0d08",
  bg1: "#2c1810",
  bg2: "#4a2a1a",
  bar: "#64320c",
  barHi: "#aa6428",
  customer: "#4169e1",
  gold: "#ffd23c",
  amber: "#ffaf1e",
  white: "#fff8eb",
  green: "#50e678",
  red: "#e63c3c",
  muted: "#8a6e55",
} as const;

export type DrinkType = "beer" | "wine" | "cocktail";

export const DRINK_TYPES: DrinkType[] = ["beer", "wine", "cocktail"];

export const DRINK_COLORS: Record<DrinkType, string> = {
  beer: "#daa520",
  wine: "#8c3741",
  cocktail: "#f05f41",
};

export const DRINK_EMOJI: Record<DrinkType, string> = {
  beer: "\u{1F37A}",
  wine: "\u{1F377}",
  cocktail: "\u{1F378}",
};

export const DRINK_LABEL: Record<DrinkType, string> = {
  beer: "BEER",
  wine: "WINE",
  cocktail: "COCKTAIL",
};

export const POSITIVE_LINES = [
  "That's sick!",
  "Yum yum!",
  "Righteous!",
  "Perfect!",
  "Heck yeah!",
  "Just what I wanted!",
  "Cheers!",
  "Stoked!",
  "Chef's kiss!",
  "Bartender of the year!",
  "You read my mind!",
];

export const NEGATIVE_LINES = [
  "Not what I ordered!",
  "This isn't right!",
  "O...kay.",
  "Ew.",
  "Wrong drink!",
  "Really?",
  "Sad times.",
  "Yuck!",
  "I'm leaving.",
];
