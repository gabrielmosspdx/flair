import { useEffect, useRef } from "react";

const STEP_MS = 1000 / 60;

export function useGameLoop(
  active: boolean,
  step: () => void,
  render: () => void,
) {
  const stepRef = useRef(step);
  const renderRef = useRef(render);

  useEffect(() => {
    stepRef.current = step;
  }, [step]);

  useEffect(() => {
    renderRef.current = render;
  }, [render]);

  useEffect(() => {
    if (!active) return;
    let raf = 0;
    let last = performance.now();
    let acc = 0;

    const loop = (now: number) => {
      raf = requestAnimationFrame(loop);
      let delta = now - last;
      last = now;
      if (delta > 250) delta = 250; // cap huge pauses
      acc += delta;
      let steps = 0;
      while (acc >= STEP_MS && steps < 5) {
        stepRef.current();
        acc -= STEP_MS;
        steps += 1;
      }
      renderRef.current();
    };

    raf = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(raf);
  }, [active]);
}
