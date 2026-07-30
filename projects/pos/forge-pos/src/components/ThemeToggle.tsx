import { motion } from 'framer-motion';
import { useTheme } from '../contexts/ThemeContext';

type ThemeMode = 'light' | 'dark' | 'system';

const MODE_ORDER: ThemeMode[] = ['light', 'dark', 'system'];
const MODE_ICONS: Record<ThemeMode, string> = {
  light: 'sun',
  dark: 'moon',
  system: 'device-desktop',
};

export default function ThemeToggle() {
  const { mode: resolvedMode, setMode, setFollowSystem, followSystem } = useTheme();

  // Derive the current mode preference from theme context
  const currentMode: ThemeMode = followSystem ? 'system' : resolvedMode;

  const cycleMode = () => {
    const idx = MODE_ORDER.indexOf(currentMode);
    const nextMode = MODE_ORDER[(idx + 1) % MODE_ORDER.length];

    if (nextMode === 'system') {
      setFollowSystem(true);
    } else {
      setFollowSystem(false);
      setMode(nextMode);
    }
  };

  // Calculate knob position based on mode
  const modeIndex = MODE_ORDER.indexOf(currentMode);
  const knobPosition = 28 + (modeIndex * 36); // 28px per segment

  return (
    <button
      onClick={cycleMode}
      className="relative w-[120px] h-[36px] rounded-full p-1 flex items-center
        cursor-pointer select-none focus-visible:ring-2 focus-visible:ring-white/60
        focus-visible:ring-offset-2 focus-visible:ring-offset-transparent
        shadow-md hover:shadow-lg active:scale-[0.92] transition-transform overflow-hidden"
      style={{
        background: resolvedMode === 'dark'
          ? 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)'
          : 'linear-gradient(135deg, #fbbf24 0%, #fb923c 100%)',
      }}
      aria-label={`Theme: ${currentMode}. Click to switch.`}
      dir="ltr"
    >
      {/* Background segments */}
      <div className="absolute inset-0 flex items-center justify-around px-2 z-10">
        {MODE_ORDER.map((m, i) => (
          <span
            key={m}
            className={`text-[10px] transition-all duration-200 ${
              i === modeIndex
                ? 'text-white'
                : resolvedMode === 'dark'
                  ? 'text-base-content/50'
                  : 'text-amber-700/60'
            }`}
          >
            <span className={'icon-[tabler--' + MODE_ICONS[m] + '] w-3.5 h-3.5'} />
          </span>
        ))}
      </div>

      {/* Sliding knob */}
      <motion.div
        className="w-[36px] h-[28px] bg-white rounded-full shadow-lg
          flex items-center justify-center z-20 absolute"
        animate={{
          left: knobPosition,
        }}
        transition={{ type: 'spring', stiffness: 400, damping: 30 }}
      >
        <span className={'icon-[tabler--' + MODE_ICONS[currentMode] + '] w-3.5 h-3.5 ' +
          (resolvedMode === 'dark' ? 'text-indigo-400' : 'text-amber-500')}
        />
      </motion.div>
    </button>
  );
}
