<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { getHealth, getProducts, getSales, type HealthStatus, type Product, type Sale } from '../api';
import { useTicketStore } from '@/utils/ticket';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import ProductSlider from '@/components/ProductSlider.vue';

const health = ref<HealthStatus | null>(null);
const products = ref<Product[]>([]);
const sales = ref<Sale[]>([]);
const loading = ref(true);
const revealed = ref(false);

/** Ticket store — its dataVersion bumps when a new order is placed, so a
 *  mounted Dashboard refetches its live stats instead of staying stale. */
const ticketStore = useTicketStore();

/** Perpetual micro-interaction: the shift clock. */
const now = ref(new Date());
const clock = computed(() =>
  now.value.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
);
const dateLine = computed(() =>
  now.value.toLocaleDateString([], { weekday: 'long', month: 'long', day: 'numeric' }),
);
let clockTimer: ReturnType<typeof setInterval> | undefined;
onMounted(() => {
  clockTimer = setInterval(() => {
    now.value = new Date();
  }, 1000);
});
onUnmounted(() => {
  if (clockTimer) {
    clearInterval(clockTimer);
  }
});

/** Fetch sales + animate the count-up (used on mount and on refresh). */
async function loadSales() {
  try {
    sales.value = await getSales();
  } catch {}
  animateCount(saleCountUp, sales.value.length);
}

onMounted(async () => {
  requestAnimationFrame(() => {
    revealed.value = true;
  });
  try {
    health.value = await getHealth();
  } catch {}
  try {
    products.value = await getProducts();
  } catch {}
  await loadSales();
  loading.value = false;
  animateCount(productCountUp, products.value.length);
});

// Refetch whenever a new order is placed (signal bumped by MenuView's ticket).
watch(
  () => ticketStore.dataVersion,
  () => {
    loadSales();
  },
);

/** Count-up: animates a stat from 0 to its target once loaded.
 *  Reduced-motion users get the final value immediately — no animation. */
const animateCount = (from: { value: number }, target: number) => {
  if (target === 0) {
    return;
  }
  if (window.matchMedia?.('(prefers-reduced-motion: reduce)').matches) {
    from.value = target;
    return;
  }
  const started = performance.now();
  const dur = 700;
  const tick = (t: number) => {
    const p = Math.min((t - started) / dur, 1);
    from.value = Math.round(target * (1 - Math.pow(1 - p, 3)));
    if (p < 1) {
      requestAnimationFrame(tick);
    }
  };
  requestAnimationFrame(tick);
};

const productCountUp = ref(0);
const saleCountUp = ref(0);

const backendOk = () => health.value?.status === 'ok';

/** Kinetic marquee band of product names. */
const marqueeNames = computed(() => {
  const names = products.value.map((p) => p.name);
  return names.length > 0 ? names : ['Formint Café'];
});
</script>

<template>
  <div class="space-y-8">
    <!-- Hero slider — featured picks with a blurred backdrop -->
    <ProductSlider v-if="!loading && products.length > 0" :products="products" />

    <!-- Asymmetric hero: title left, shift clock right -->
    <div
      class="pos-reveal flex flex-wrap items-end justify-between gap-6"
      :class="revealed ? 'is-visible' : ''"
    >
      <div>
        <p class="eyebrow">Overview</p>
        <h1 class="mt-3 max-w-2xl text-3xl font-bold tracking-tight md:text-4xl">
          The register at a glance
        </h1>
        <p class="mt-1 text-sm text-base-content/50">Menu, orders, and backend health — live.</p>
      </div>
      <div class="bezel">
        <div class="bezel-core px-5 py-3 text-right">
          <p class="font-mono text-[0.65rem] font-semibold uppercase tracking-[0.2em] text-base-content/50">
            {{ dateLine }}
          </p>
          <p class="stat-value-display mt-1 text-3xl tabular-nums">{{ clock }}</p>
        </div>
      </div>
    </div>

    <!-- Asymmetric stat grid (shadcn cards) -->
    <div class="grid grid-cols-1 gap-6 md:grid-cols-3">
      <Card class="pos-reveal md:col-span-2" :class="revealed ? 'is-visible' : ''" style="transition-delay: 90ms">
        <CardHeader class="flex-row items-center justify-between space-y-0">
          <div>
            <CardTitle class="text-sm font-semibold uppercase tracking-widest text-muted-foreground">Catalog</CardTitle>
            <CardDescription>Products live from the POS API</CardDescription>
          </div>
          <Badge variant="outline">{{ products.length }} items</Badge>
        </CardHeader>
        <CardContent>
          <Skeleton v-if="loading" class="h-14 w-24" />
          <p v-else class="stat-value-display text-5xl">{{ productCountUp }}</p>
        </CardContent>
      </Card>

      <Card class="pos-reveal" :class="revealed ? 'is-visible' : ''" style="transition-delay: 180ms">
        <CardHeader class="flex-row items-center justify-between space-y-0">
          <div>
            <CardTitle class="text-sm font-semibold uppercase tracking-widest text-muted-foreground">Orders</CardTitle>
            <CardDescription>Recent transactions</CardDescription>
          </div>
          <Badge variant="secondary">{{ sales.length }}</Badge>
        </CardHeader>
        <CardContent>
          <Skeleton v-if="loading" class="h-14 w-24" />
          <p v-else class="stat-value-display text-5xl">{{ saleCountUp }}</p>
        </CardContent>
      </Card>

      <Card class="pos-reveal" :class="revealed ? 'is-visible' : ''" style="transition-delay: 270ms">
        <CardHeader class="flex-row items-center justify-between space-y-0">
          <div>
            <CardTitle class="text-sm font-semibold uppercase tracking-widest text-muted-foreground">Backend</CardTitle>
            <CardDescription>{{ health?.service || 'Not connected' }}</CardDescription>
          </div>
          <Badge v-if="!loading" :variant="backendOk() ? 'success' : 'destructive'">
            {{ backendOk() ? 'OK' : 'OFF' }}
          </Badge>
          <Skeleton v-else class="h-5 w-12 rounded-full" />
        </CardHeader>
        <CardContent>
          <Skeleton v-if="loading" class="h-14 w-24" />
          <div v-else class="flex items-center gap-3">
            <span
              class="fu-breath h-3 w-3 rounded-full"
              :class="backendOk() ? 'bg-success' : 'bg-error'"
            />
            <p class="stat-value-display text-5xl" :class="backendOk() ? 'text-success' : 'text-error'">
              {{ backendOk() ? 'OK' : 'OFF' }}
            </p>
          </div>
        </CardContent>
      </Card>

      <Card class="pos-reveal md:col-span-2" :class="revealed ? 'is-visible' : ''" style="transition-delay: 360ms">
        <CardHeader>
          <CardTitle class="text-sm font-semibold uppercase tracking-widest text-muted-foreground">Quick actions</CardTitle>
          <CardDescription>Jump straight into the register.</CardDescription>
        </CardHeader>
        <CardContent class="flex flex-wrap gap-3">
          <Button as-child>
            <router-link to="/menu">Browse Menu</router-link>
          </Button>
          <Button variant="outline" as-child>
            <router-link to="/orders">View Orders</router-link>
          </Button>
          <Button variant="ghost" as-child>
            <router-link to="/settings">Settings</router-link>
          </Button>
        </CardContent>
      </Card>
    </div>

    <!-- Kinetic marquee — the day's menu, endlessly in motion -->
    <div v-if="!loading" class="pos-reveal" :class="revealed ? 'is-visible' : ''">
      <div class="fu-marquee rounded-full border border-base-300/70 bg-base-100/70 py-2.5">
        <div class="fu-marquee-track gap-8 pr-8">
          <template v-for="n in 2" :key="n">
            <span
              v-for="(name, i) in [...marqueeNames, ...marqueeNames]"
              :key="`${n}-${i}`"
              class="whitespace-nowrap font-mono text-[0.65rem] font-semibold uppercase tracking-[0.2em] text-base-content/45"
            >
              {{ name }} <span class="text-primary">✦</span>
            </span>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>
