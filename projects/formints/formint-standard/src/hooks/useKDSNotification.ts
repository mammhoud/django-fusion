import { useEffect, useRef, useCallback } from 'react';
import { KitchenTicket } from '../types';

export type ChimeVariant = 'chime1' | 'chime2' | 'chime3';

export const CHIME_VARIANTS: { id: ChimeVariant; label: string }[] = [
  { id: 'chime1', label: 'Classic (C↗E)' },
  { id: 'chime2', label: 'Bright (G↗C)' },
  { id: 'chime3', label: 'Deep (A↘E)' },
];

/**
 * Play a chime via the Web Audio API. Three variants available.
 * No external audio files needed.
 */
function playChime(variant: ChimeVariant = 'chime1') {
  try {
    const ctx = new AudioContext();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.connect(gain);
    gain.connect(ctx.destination);

    osc.type = 'sine';

    switch (variant) {
      case 'chime2':
        // Bright: G4 → C5  (perfect-fourth ascending, brighter feel)
        osc.frequency.setValueAtTime(392.00, ctx.currentTime);
        osc.frequency.setValueAtTime(523.25, ctx.currentTime + 0.10);
        gain.gain.setValueAtTime(0.22, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.30);
        osc.start(ctx.currentTime);
        osc.stop(ctx.currentTime + 0.30);
        break;
      case 'chime3':
        // Deep: A3 → E3  (descending perfect-fourth, deeper alert)
        osc.frequency.setValueAtTime(220.00, ctx.currentTime);
        osc.frequency.setValueAtTime(164.81, ctx.currentTime + 0.15);
        gain.gain.setValueAtTime(0.28, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.40);
        osc.start(ctx.currentTime);
        osc.stop(ctx.currentTime + 0.40);
        break;
      case 'chime1':
      default:
        // Classic: C5 → E5  (pleasant major-third ascending)
        osc.frequency.setValueAtTime(523.25, ctx.currentTime);
        osc.frequency.setValueAtTime(659.25, ctx.currentTime + 0.12);
        gain.gain.setValueAtTime(0.25, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.35);
        osc.start(ctx.currentTime);
        osc.stop(ctx.currentTime + 0.35);
    }
  } catch {
    // Web Audio API unavailable — silently skip
  }
}

/**
 * Request permission for the Notification API (native OS notifications).
 * Tauri webviews support this — it works on macOS, Windows, and Linux.
 */
function requestNotificationPermission() {
  if (!('Notification' in window)) return; // not supported
  if (Notification.permission === 'default') {
    Notification.requestPermission().catch(() => {});
  }
}

/**
 * Show a native OS notification via the Notification API.
 * Falls back silently if not supported or permission was denied.
 */
function showNativeNotification(ticket: KitchenTicket) {
  if (!('Notification' in window)) return;
  if (Notification.permission !== 'granted') return;

  const orderTypeLabel =
    ticket.priority === 1 ? 'Dine-in' :
    ticket.priority === 2 ? 'Takeaway' :
    ticket.priority === 3 ? 'Delivery' : 'Order';

  try {
    const notif = new Notification(`New ${orderTypeLabel} Order`, {
      body: `Order #${ticket.sale_id} is pending — ${ticket.prepare_time_minutes}min est. prep time`,
      // Omit icon — the Tauri webview doesn't reliably serve /favicon.png
      tag: `kds-order-${ticket.sale_id}`, // prevents duplicate notifications for the same order
    });
    // Focus the app window when the notification is clicked
    notif.onclick = () => {
      window.focus();
      notif.close();
    };
  } catch {
    // Notification API unavailable — silently skip
  }
}

/**
 * useKDSNotification
 *
 * Monitors the `tickets` array for new `pending` tickets that were not
 * present in the previous render cycle. When detected, it:
 *  1. Plays a short chime via the Web Audio API
 *  2. Flashes the document title bar ("New Order!" ↔ original title)
 *  3. Shows a native OS notification if the window is minimized/hidden
 *
 * The title flash stops automatically when the window regains focus or
 * after 15 seconds, whichever comes first.
 *
 * @param tickets - Current array of kitchen tickets from the backend poll.
 * @param mutedUntil - Timestamp (ms) until which notifications are muted.
 */
export function useKDSNotification(tickets: KitchenTicket[], mutedUntil: number | null = null, chimeVariant: ChimeVariant = 'chime1') {
  // Keep a set of all known ticket IDs across renders
  const knownIdsRef = useRef<Set<number>>(new Set());
  // Interval handle for the title flash
  const flashRef = useRef<ReturnType<typeof setInterval> | null>(null);
  // Stored original title so we can restore it
  const originalTitleRef = useRef<string>(document.title);
  // Guard against multiple simultaneous flash cycles
  const isFlashingRef = useRef(false);

  const stopFlash = useCallback(() => {
    if (flashRef.current) {
      clearInterval(flashRef.current);
      flashRef.current = null;
    }
    document.title = originalTitleRef.current;
    isFlashingRef.current = false;
  }, []);

  const startFlash = useCallback(() => {
    if (isFlashingRef.current) return; // already flashing
    isFlashingRef.current = true;
    originalTitleRef.current = document.title;

    let showAlert = true;
    flashRef.current = setInterval(() => {
      document.title = showAlert
        ? 'New Order!'
        : originalTitleRef.current;
      showAlert = !showAlert;
    }, 800);

    // Auto-stop after 15 seconds even if the tab stays hidden
    setTimeout(() => {
      if (isFlashingRef.current) stopFlash();
    }, 15000);
  }, [stopFlash]);

  // ── Detect new pending tickets ──
  useEffect(() => {
    const nowIds = new Set(tickets.filter(t => t.status === 'pending').map(t => t.id));
    const prevIds = knownIdsRef.current;
    const wasEmpty = prevIds.size === 0;

    // Find any pending ticket ID that wasn't in the previous set
    let foundNew = false;
    for (const id of nowIds) {
      if (!prevIds.has(id)) {
        foundNew = true;
        break;
      }
    }

    // Update the known set for the next diff
    knownIdsRef.current = new Set([...prevIds, ...tickets.map(t => t.id)]);

    // Trigger notification only if:
    //   - A genuinely new pending ticket arrived
    //   - This is NOT the very first load (prevIds was empty → initial render)
    //   - Notifications are not muted
    const isMuted = mutedUntil && mutedUntil > Date.now();
    if (foundNew && !wasEmpty && !isMuted) {
      playChime(chimeVariant);
      startFlash();
      // If the window is minimized or in the background, fire a native OS
      // notification as well (the tab-title flash won't be visible).
      if (document.hidden) {
        // Find the first new ticket for the notification body
        const newTicket = tickets.find(t => t.status === 'pending' && !prevIds.has(t.id));
        if (newTicket) showNativeNotification(newTicket);
      }
    }
  }, [tickets, startFlash]);

  // ── Request permission for native OS notifications on mount ──
  useEffect(() => {
    requestNotificationPermission();
  }, []);

  // ── Stop flashing when the window regains focus ──
  useEffect(() => {
    const onFocus = () => stopFlash();
    window.addEventListener('focus', onFocus);
    return () => {
      window.removeEventListener('focus', onFocus);
      stopFlash();
    };
  }, [stopFlash]);
}
