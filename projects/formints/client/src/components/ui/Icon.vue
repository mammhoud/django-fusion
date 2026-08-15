<script setup lang="ts">
/**
 * Icon — thin-stroke glyph set for the POS register, matching the storefront's
 * hand-rolled icon language: 1.5px precise lines, currentColor, no icon
 * library. Size and color come from the class (h-4 w-4, text-* etc.);
 * stroke is inherited from the root so every glyph reads at the same weight.
 */
interface Props {
  name: string;
}
defineProps<Props>();

const MARKUP: Record<string, string> = {
  plus: '<path d="M12 5v14M5 12h14"/>',
  minus: '<path d="M5 12h14"/>',
  search: '<circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/>',
  check: '<path d="M20 6 9 17l-5-5"/>',
  x: '<path d="M18 6 6 18M6 6l12 12"/>',
  loader: '<path d="M21 12a9 9 0 1 1-6.2-8.56"/>',
  'chevron-left': '<path d="m15 18-6-6 6-6"/>',
  'chevron-right': '<path d="m9 18 6-6-6-6"/>',
  'chevron-down': '<path d="m6 9 6 6 6-6"/>',
  'chevrons-up-down': '<path d="m7 15 5 5 5-5M7 9l5-5 5 5"/>',
  printer:
    '<path d="M6 9V3h12v6"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><path d="M6 14h12v8H6z"/>',
  'cooking-pot':
    '<path d="M2 12h20"/><path d="M20 12v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-8"/><path d="m4 8 16-4"/><path d="m8.9 6.8-.5-1.9a2 2 0 0 1 1.5-2.4l1.9-.5a2 2 0 0 1 2.4 1.5l.5 1.9"/>',
  sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
  moon: '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>',
};
</script>

<template>
  <svg
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="1.5"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
    v-html="MARKUP[name]"
  />
</template>
