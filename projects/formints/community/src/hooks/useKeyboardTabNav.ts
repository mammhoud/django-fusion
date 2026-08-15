import { useCallback } from 'react';

/**
 * Arrow-key keyboard navigation for tab lists.
 *
 * Adds Left/Right (or Up/Down) arrow key support for cycling through tabs,
 * plus Home/End to jump to the first/last tab.
 *
 * @param tabKeys   Ordered array of tab identifiers (strings).
 * @param activeTab Currently active tab identifier.
 * @param onSelect  Callback fired when a new tab should be selected.
 * @returns         `onKeyDown` handler to attach to the tablist <nav>.
 */
export function useKeyboardTabNav<T extends string>(
  tabKeys: readonly T[],
  activeTab: T,
  onSelect: (tab: T) => void,
): { onKeyDown: (e: React.KeyboardEvent) => void } {
  const onKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      // Ignore when focus is inside an input/textarea
      if (
        e.target instanceof HTMLInputElement ||
        e.target instanceof HTMLTextAreaElement
      ) {
        return;
      }

      const currentIdx = tabKeys.indexOf(activeTab);
      if (currentIdx === -1) return;

      let nextIdx: number | null = null;

      switch (e.key) {
        case 'ArrowLeft':
        case 'ArrowUp':
          e.preventDefault();
          nextIdx = currentIdx > 0 ? currentIdx - 1 : tabKeys.length - 1;
          break;
        case 'ArrowRight':
        case 'ArrowDown':
          e.preventDefault();
          nextIdx = currentIdx < tabKeys.length - 1 ? currentIdx + 1 : 0;
          break;
        case 'Home':
          e.preventDefault();
          nextIdx = 0;
          break;
        case 'End':
          e.preventDefault();
          nextIdx = tabKeys.length - 1;
          break;
      }

      if (nextIdx !== null && nextIdx !== currentIdx) {
        const nextTab = tabKeys[nextIdx];
        if (nextTab) {
          onSelect(nextTab);
          // Focus the newly selected tab button
          const tabButton = document.getElementById(
            `${(e.currentTarget as HTMLElement).dataset.tabPrefix || 'tab'}-${nextTab}`,
          ) as HTMLButtonElement | null;
          tabButton?.focus();
        }
      }
    },
    [tabKeys, activeTab, onSelect],
  );

  return { onKeyDown };
}
