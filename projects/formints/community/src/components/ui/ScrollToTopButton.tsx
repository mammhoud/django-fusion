import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

/**
 * Floating "scroll to top" button pinned to the bottom-right corner.
 *
 * - Appears (springs in) once the window is scrolled ~400px down, fades out at top.
 * - Sits to the LEFT of the ChatSupport FAB (bottom-6 right-24) so the two never
 *   overlap, and mirrors to the left corner in RTL layouts.
 * - While hidden it is removed from tab order and the a11y tree.
 */
export default function ScrollToTopButton() {
  const { t } = useTranslation();
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const onScroll = () => {
      setVisible((window.scrollY || document.documentElement.scrollTop || 0) > 400);
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const label = t('common.scrollToTop') || 'Scroll to top';

  return (
    <button
      type="button"
      onClick={scrollToTop}
      aria-label={label}
      title={label}
      aria-hidden={!visible}
      tabIndex={visible ? 0 : -1}
      className={`fixed bottom-6 right-24 rtl:right-auto rtl:left-24 z-40 w-11 h-11 rounded-full
        bg-base-100/80 backdrop-blur-md border border-base-300/40 text-base-content/70
        shadow-lg hover:shadow-xl hover:text-primary hover:border-primary/40
        flex items-center justify-center transition-all duration-300 ease-out
        active:scale-90 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary
        ${visible
          ? 'opacity-100 translate-y-0 scale-100'
          : 'opacity-0 translate-y-3 scale-90 pointer-events-none'
        }`}
    >
      <span className="ri-arrow-up-line ri-20px" />
    </button>
  );
}
