# Flair Web (React / Mobile)

A React + TypeScript port of the Flair pygame arcade game, optimized for
mobile browsers. Rendered with HTML5 Canvas for smooth 60fps on phones.

## Gameplay

Tap anywhere on the playfield to throw your currently-selected drink toward
that spot. Match the drink emoji that each customer is demanding before they
reach the bar at the center of the screen.

- **3 drink types:** Beer, Wine, Cocktail (each starts with 5 in stock).
- **Pick a drink** from the bottom bar before throwing.
- **Restock** refills all drinks (3-second pause).
- **Wrong drink or a customer reaching the bar** = lose a life (3 total).
- Waves get faster and bigger. Score scales with wave.

### Controls

- **Touch / mouse:** tap the playfield to throw; on-screen buttons to pick
  drinks, restock, pause, quit.
- **Keyboard** (optional, for desktop): `1`/`2`/`3` select drink, `R` restock,
  `P` pause, `Esc` quit.

## Running locally

```bash
cd web
npm install
npm run dev          # http://localhost:5173
```

## Production build

```bash
cd web
npm install
npm run build        # outputs static site to web/dist
npm run preview      # serve the built site
```

The built bundle is a pure static site (no server needed) and can be hosted
on Vercel, Netlify, GitHub Pages, or any static host.

## Architecture

```
web/
├── index.html                 Mobile-optimized viewport meta
├── src/
│   ├── main.tsx               React entry
│   ├── App.tsx                Scene routing + high score persistence
│   ├── styles.css             Mobile-first styles, safe-area insets
│   ├── hooks/
│   │   └── useGameLoop.ts     Fixed-timestep 60Hz loop via rAF
│   ├── game/
│   │   ├── constants.ts       All game tuning values (mirrors pygame)
│   │   ├── types.ts           Game state + entity shapes
│   │   ├── engine.ts          Update loop, spawning, collisions, waves
│   │   └── render.ts          Canvas drawing + view transform
│   └── components/
│       ├── MenuScene.tsx
│       ├── GameCanvas.tsx     Canvas element + DPR sizing + input
│       ├── HUD.tsx            React overlay: score, lives, drinks, restock
│       └── GameOverScene.tsx
```

- **Game state is a plain mutable object held in a `useRef`.** The game loop
  mutates it at 60Hz in the `useGameLoop` rAF callback. React only re-renders
  the HUD when values actually change (change-detection in `handleTick`).
- **Canvas renders the world**; React renders the HUD/menus. This keeps 60fps
  rendering off the React reconciliation path.
- **Responsive scaling:** the world is 1200×800 logical units; `computeTransform`
  fits it into the viewport with letterboxing. Pointer coordinates are mapped
  back through `screenToWorld`.
- **Fixed timestep** with an accumulator so physics stay stable across
  variable device frame rates, with a 5-step cap to avoid the spiral of death.

## Parity with pygame version

The web port matches the pygame balancing numbers in `src/game/constants.ts`:

| Mechanic | Value |
| --- | --- |
| Initial lives | 3 |
| Starting inventory (each drink) | 5 |
| Initial wave size | 8 (+2 per wave, cap 20) |
| Base spawn delay | 120 frames (−8/wave, floor 30) |
| Base customer speed | 0.5 × 1.05^(wave−1) px/frame |
| Projectile speed | 6 px/frame (max life 150) |
| Restock duration | 180 frames (3 s) |
| Base points | 10 + (wave−1)×2 |

Differences from the desktop version:

- No sprite sheets — customers/projectiles are drawn procedurally to keep the
  download size tiny.
- No gamepad support (mobile-first). Keyboard is available on desktop.
- High scores stored in `localStorage` instead of the `saves/` directory.
- Landscape or portrait both work; the world is letterboxed to fit.
