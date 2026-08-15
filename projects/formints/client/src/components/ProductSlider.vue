<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import Icon from '@/components/ui/Icon.vue';
import type { Product } from '../api';

const props = defineProps<{ products: Product[] }>();

/** Slides = featured picks first (up to 5), falling back to the full menu. */
const slides = computed(() => {
  const featured = props.products.filter((p) => p.is_featured).slice(0, 5);
  return (featured.length ? featured : props.products).slice(0, 5);
});

const i = ref(0);
const paused = ref(false);
let timer: ReturnType<typeof setInterval> | undefined;

/** Letter-tile guard for products without imagery — matches MenuView. */
const letterTile = (name: string) => name.trim().charAt(0).toUpperCase() || '•';

function go(n: number) {
  if (slides.value.length === 0) {
    return;
  }
  i.value = (n + slides.value.length) % slides.value.length;
}
const next = () => go(i.value + 1);
const prev = () => go(i.value - 1);

function start() {
  stop();
  if (window.matchMedia?.('(prefers-reduced-motion: reduce)').matches) {
    return;
  }
  timer = setInterval(() => {
    if (!paused.value) {
      next();
    }
  }, 6000);
}
function stop() {
  if (timer) {
    clearInterval(timer);
    timer = undefined;
  }
}

onMounted(start);
onUnmounted(stop);
</script>

<template>
  <div
    v-if="slides.length > 0"
    class="bezel pos-reveal"
    :class="paused ? '' : ''"
    @mouseenter="paused = true"
    @mouseleave="paused = false"
  >
    <div class="bezel-core relative overflow-hidden">
      <!-- Blurred backdrop — active slide's photo, cross-faded behind. -->
      <div class="pointer-events-none absolute inset-0" aria-hidden="true">
        <template v-for="(p, pi) in slides" :key="`bg-${p.id}`">
          <img
            v-if="p.image"
            :src="p.image"
            alt=""
            class="absolute inset-0 h-full w-full scale-110 object-cover blur-2xl transition-opacity duration-1000 ease-[cubic-bezier(0.32,0.72,0,1)]"
            :class="i === pi ? 'opacity-70' : 'opacity-0'"
          />
          <div
            v-else
            class="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-base-200 to-base-300/80 transition-opacity duration-1000 ease-[cubic-bezier(0.32,0.72,0,1)]"
            :class="i === pi ? 'opacity-70' : 'opacity-0'"
          >
            <span class="font-display text-6xl font-bold text-base-content/15">{{ letterTile(p.name) }}</span>
          </div>
        </template>
        <div class="absolute inset-0 bg-base-100/80 dark:bg-base-300/80"></div>
      </div>

      <!-- Slide body: sharp image left, copy right. -->
      <div class="relative grid min-h-[20rem] items-center gap-8 p-7 sm:p-10 md:grid-cols-[minmax(0,15rem)_1fr]">
        <div class="relative mx-auto w-full max-w-[15rem]">
          <div class="relative aspect-square overflow-hidden rounded-[1.5rem] border border-base-300/60 shadow-[0_24px_48px_-24px_hsl(var(--pos-ink)/0.25)]">
            <template v-for="(p, pi) in slides" :key="`fg-${p.id}`">
              <img
                v-if="p.image"
                :src="p.image"
                :alt="p.name"
                loading="lazy"
                class="absolute inset-0 h-full w-full object-cover transition-all duration-1000 ease-[cubic-bezier(0.32,0.72,0,1)]"
                :class="i === pi ? 'scale-100 opacity-100' : 'scale-[1.04] opacity-0'"
              />
              <div
                v-else
                class="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-base-200 to-base-300/80 transition-all duration-1000 ease-[cubic-bezier(0.32,0.72,0,1)]"
                :class="i === pi ? 'scale-100 opacity-100' : 'scale-[1.04] opacity-0'"
              >
                <span class="font-display text-5xl font-bold text-base-content/15">{{ letterTile(p.name) }}</span>
              </div>
            </template>
            <span class="fu-breath absolute right-4 top-4 h-2 w-2 rounded-full bg-primary"></span>
          </div>
        </div>

        <!-- Slide copy -->
        <div class="relative min-h-[11rem]">
          <template v-for="(p, pi) in slides" :key="`copy-${p.id}`">
            <div
              v-show="i === pi"
              class="absolute inset-0 transition-all duration-700 ease-[cubic-bezier(0.32,0.72,0,1)]"
              :class="i === pi ? 'translate-y-0 opacity-100' : 'translate-y-3 opacity-0'"
            >
              <p class="eyebrow">{{ p.category || 'Today' }}</p>
              <h2 class="mt-4 font-display text-2xl font-bold tracking-tight sm:text-3xl">
                {{ p.name }}
              </h2>
              <p class="mt-2 font-mono text-[0.65rem] font-semibold uppercase tracking-[0.2em] text-base-content/45">
                {{ p.is_featured ? 'Featured pick' : 'On the menu' }} · {{ p.unit || 'each' }}
              </p>
              <p class="stat-value-display mt-5 text-3xl text-primary">
                ${{ p.price.toFixed(2) }}
              </p>
            </div>
          </template>
        </div>
      </div>

      <!-- Controls: arrows + dots -->
      <div class="relative flex items-center justify-between gap-4 border-t border-base-300/50 px-7 py-4">
        <div class="flex items-center gap-2">
          <button
            type="button"
            class="flex h-9 w-9 items-center justify-center rounded-full border border-base-300 bg-base-100 text-base-content transition-all duration-300 ease-[cubic-bezier(0.32,0.72,0,1)] hover:border-base-content/40 active:scale-95"
            :aria-label="'Previous slide'"
            @click="prev"
          >
            <Icon name="chevron-left" class="h-4 w-4" />
          </button>
          <button
            type="button"
            class="flex h-9 w-9 items-center justify-center rounded-full border border-base-300 bg-base-100 text-base-content transition-all duration-300 ease-[cubic-bezier(0.32,0.72,0,1)] hover:border-base-content/40 active:scale-95"
            :aria-label="'Next slide'"
            @click="next"
          >
            <Icon name="chevron-right" class="h-4 w-4" />
          </button>
        </div>

        <div class="flex items-center gap-2">
          <button
            v-for="(p, pi) in slides"
            :key="`dot-${p.id}`"
            type="button"
            class="h-1.5 rounded-full transition-all duration-500 ease-[cubic-bezier(0.32,0.72,0,1)]"
            :class="i === pi ? 'w-8 bg-primary' : 'w-1.5 bg-base-content/20 hover:bg-base-content/40'"
            :aria-label="`Go to slide ${pi + 1}`"
            @click="go(pi)"
          ></button>
          <p class="ml-3 font-mono text-[0.65rem] uppercase tracking-widest text-base-content/45">
            {{ String(i + 1).padStart(2, '0') }} / {{ String(slides.length).padStart(2, '0') }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
