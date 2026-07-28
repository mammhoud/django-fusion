import { motion } from 'framer-motion';
import { useTheme } from '../contexts/ThemeContext';

export default function ThemeToggle() {
  const { mode, toggleMode } = useTheme();
  const isDark = mode === 'dark';

  return (
    <motion.button
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.92 }}
      onClick={toggleMode}
      className="relative w-[72px] h-[36px] rounded-full p-1 flex items-center
        cursor-pointer select-none focus-visible:ring-2 focus-visible:ring-white/60 focus-visible:ring-offset-2 focus-visible:ring-offset-transparent
        shadow-md hover:shadow-lg"
      style={{
        background: isDark
          ? 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)'
          : 'linear-gradient(135deg, #fbbf24 0%, #fb923c 100%)',
        boxShadow: isDark
          ? '0 2px 8px rgba(15, 23, 42, 0.4)'
          : '0 2px 8px rgba(251, 191, 36, 0.3)',
      }}
      aria-label={`Switch to ${isDark ? 'light' : 'dark'} mode`}
    >
      {/* Subtle inner glow overlay */}
      <span className="absolute inset-0 rounded-full bg-white/5 pointer-events-none" />

      {/* Background icon hint — logical properties for RTL support */}
      <span
        className="absolute text-[10px] pointer-events-none select-none flex items-center z-10"
        style={{
          insetInlineStart: isDark ? 'auto' : '10px',
          insetInlineEnd: isDark ? '10px' : 'auto',
          color: isDark ? 'rgba(148,163,184,0.7)' : 'rgba(255,255,255,0.9)',
        }}
      >
        {isDark ? (
          <span className="icon-[tabler--moon] w-3 h-3" />
        ) : (
          <span className="icon-[tabler--sun] w-3 h-3" />
        )}
      </span>

      {/* Sliding knob - snaps instantly */}
      <div
        className="w-[28px] h-[28px] bg-white rounded-full shadow-lg 
          flex items-center justify-center z-20"
        style={{
          transform: isDark ? 'translateX(36px)' : 'translateX(0)',
        }}
      >
        {isDark ? (
          <span className="icon-[tabler--moon] w-3.5 h-3.5 text-indigo-400" />
        ) : (
          <span className="icon-[tabler--sun] w-3.5 h-3.5 text-amber-500" />
        )}
      </div>
    </motion.button>
  );
}
