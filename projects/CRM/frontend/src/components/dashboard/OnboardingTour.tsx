import { useEffect, useState } from 'react';

const STEPS = [
  ['NAVIGATOR', 'Use the sidebar to move between CRM, marketing, finance, people, reports, and workspace controls.'],
  ['COMMAND', 'Press Ctrl/Cmd + K to search routes and live workspace records.'],
  ['DOSSIERS', 'Open People to review member activity, deals, posts, and invoice performance.'],
];

export default function OnboardingTour() {
  const [step, setStep] = useState(0);
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    if (localStorage.getItem('loop-crm:onboarding:v1') !== 'done') setVisible(true);
  }, []);
  const close = () => { localStorage.setItem('loop-crm:onboarding:v1', 'done'); setVisible(false); };
  if (!visible) return null;
  const [label, copy] = STEPS[step];
  return <div className="loop-tour" role="dialog" aria-modal="true" aria-label="Loop CRM quick start"><div className="loop-tour__panel"><span className="loop-tour__index">0{step + 1} / 0{STEPS.length}</span><span className="loop-tour__kicker">{label}</span><h2>OPERATE THE WORKSPACE</h2><p>{copy}</p><div className="loop-tour__actions"><button type="button" onClick={close}>SKIP</button>{step < STEPS.length - 1 ? <button type="button" onClick={() => setStep(step + 1)}>NEXT →</button> : <button type="button" onClick={close}>ENTER WORKSPACE →</button>}</div></div></div>;
}
