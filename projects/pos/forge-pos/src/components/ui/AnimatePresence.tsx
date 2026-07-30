import { useState, useRef, useEffect, type ReactNode } from 'react';

interface Props { mode?: 'wait' | 'sync'; children: ReactNode; initial?: boolean; }

/** CSS-based AnimatePresence — handles exit animations via animationend events. */
export default function AnimatePresence({ children, mode = 'sync' }: Props) {
  const [exitingChild, setExitingChild] = useState<ReactNode>(null);
  const [currentChild, setCurrentChild] = useState<ReactNode>(children);
  const exitRef = useRef<HTMLDivElement>(null);
  const prevRef = useRef<ReactNode>(children);

  useEffect(() => {
    if (children !== prevRef.current && prevRef.current !== null) {
      if (mode === 'wait') setExitingChild(prevRef.current);
      else { setExitingChild(prevRef.current); setCurrentChild(children); }
    } else { setCurrentChild(children); setExitingChild(null); }
    prevRef.current = children;
  }, [children, mode]);

  return (
    <>
      {exitingChild && (
        <div ref={exitRef} className="animate-fade-out"
          onAnimationEnd={() => { setExitingChild(null); if (mode === 'wait') setCurrentChild(children); }}
          style={{ pointerEvents: 'none' }}>
          {exitingChild}
        </div>
      )}
      {mode === 'wait' && exitingChild ? null : currentChild}
    </>
  );
}
