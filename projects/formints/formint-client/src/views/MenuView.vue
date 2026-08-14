<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue';
import { Plus, Minus, Search, Check, Loader2, X } from 'lucide-vue-next';
import { getProducts, createOrder, type Product } from '../api';
import { useScrollMotion } from '../utils/scrollMotion';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

const items = ref<Product[]>([]);
const loading = ref(true);
const revealed = ref(false);
const query = ref('');
const activeCategory = ref('all');

const { refresh, dispose } = useScrollMotion();

/** Categories present in the catalog, ordered by first appearance. */
const categories = computed(() => {
  const seen: string[] = [];
  for (const p of items.value) {
    if (p.category && !seen.includes(p.category)) {
      seen.push(p.category);
    }
  }
  return seen;
});

/** Search + category filter — keeps the bento shape predictable. */
const filtered = computed(() => {
  const q = query.value.trim().toLowerCase();
  return items.value.filter((p) => {
    if (activeCategory.value !== 'all' && p.category !== activeCategory.value) {
      return false;
    }
    if (!q) {
      return true;
    }
    return p.name.toLowerCase().includes(q) || p.category?.toLowerCase().includes(q);
  });
});

/** Local ticket — quantities per product, running total. */
const ticket = ref<Record<number, number>>({});
const totalItems = computed(() => Object.values(ticket.value).reduce((a, b) => a + b, 0));
const totalPrice = computed(() =>
  Object.entries(ticket.value).reduce((a, [id, qty]) => {
    const p = items.value.find((x) => x.id === Number(id));
    return a + (p ? p.price * qty : 0);
  }, 0),
);

/** Order type — mirrors the backend Order.OrderType choices. */
const ORDER_TYPES = [
  { value: 'takeaway', label: 'Takeaway' },
  { value: 'dine_in', label: 'Dine in' },
  { value: 'delivery', label: 'Delivery' },
];
const orderType = ref('takeaway');

const submitting = ref(false);
const submitError = ref('');
const placedReference = ref('');

async function placeOrder() {
  if (submitting.value || totalItems.value === 0) {
    return;
  }
  submitting.value = true;
  submitError.value = '';
  placedReference.value = '';
  try {
    const order = await createOrder({
      items: Object.entries(ticket.value).map(([id, quantity]) => ({
        product_id: Number(id),
        quantity,
      })),
      order_type: orderType.value,
      customer_name: 'Guest',
    });
    placedReference.value = order.reference;
    ticket.value = {};
  } catch (err) {
    submitError.value = err instanceof Error ? err.message : 'Could not place the order.';
  } finally {
    submitting.value = false;
  }
}

function add(id: number) {
  ticket.value = { ...ticket.value, [id]: (ticket.value[id] ?? 0) + 1 };
}
function remove(id: number) {
  const next = { ...ticket.value };
  if ((next[id] ?? 0) <= 1) {
    delete next[id];
  } else {
    next[id] -= 1;
  }
  ticket.value = next;
}
const qty = (id: number) => ticket.value[id] ?? 0;

const money = (n: number) => `$${n.toFixed(2)}`;

/** Bento spans: a 2×2 image-led lead tile, dense-filled around it. */
const cardSpan = (i: number) =>
  i === 0 ? 'sm:col-span-2 sm:row-span-2' : '';

/** Letter-tile fallback for products without imagery. */
const letterTile = (name: string) => name.trim().charAt(0).toUpperCase() || '•';

onMounted(async () => {
  requestAnimationFrame(() => {
    revealed.value = true;
  });
  try {
    items.value = await getProducts();
    await nextTick();
    refresh(document.getElementById('menu-grid') ?? document.body);
  } catch {
    /* empty state below */
  }
  loading.value = false;
  await nextTick();
  refresh(document.getElementById('menu-grid') ?? document.body);
});

onUnmounted(() => dispose());
</script>

<template>
  <div class="space-y-8">
    <!-- Asymmetric header: search floats right, title anchors left -->
    <div
      class="pos-reveal flex flex-wrap items-end justify-between gap-6"
      :class="revealed ? 'is-visible' : ''"
    >
      <div class="max-w-xl">
        <p class="eyebrow">Register</p>
        <h1 class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">Menu</h1>
        <p class="mt-2 text-sm text-base-content/50">
          Tap an item to add it to the ticket — the running total tracks below.
        </p>
      </div>

      <div class="bezel w-full sm:w-72">
        <div class="bezel-core flex items-center gap-2 px-3 py-2">
          <Search class="h-4 w-4 shrink-0 text-base-content/40" />
          <input
            v-model="query"
            type="search"
            placeholder="Search the menu…"
            class="w-full bg-transparent text-sm outline-none placeholder:text-base-content/40"
          />
        </div>
      </div>
    </div>

    <!-- Kinetic marquee category band -->
    <div
      v-if="categories.length > 0"
      class="pos-reveal"
      :class="revealed ? 'is-visible' : ''"
    >
      <div class="fu-marquee rounded-full border border-base-300/70 bg-base-100/70 py-2.5">
        <div class="fu-marquee-track gap-8 pr-8">
          <template v-for="n in 2" :key="n">
            <span
              v-for="(c, i) in [...categories, ...categories]"
              :key="`${n}-${i}`"
              class="font-mono text-[0.65rem] font-semibold uppercase tracking-[0.2em] text-base-content/45"
            >
              {{ c }} <span class="text-primary">✦</span>
            </span>
          </template>
        </div>
      </div>
    </div>

    <!-- Category pills -->
    <div
      v-if="categories.length > 0"
      class="pos-reveal flex flex-wrap items-center gap-2"
      :class="revealed ? 'is-visible' : ''"
    >
      <Button
        size="sm"
        :variant="activeCategory === 'all' ? 'default' : 'outline'"
        @click="activeCategory = 'all'"
      >
        All
      </Button>
      <Button
        v-for="c in categories"
        :key="c"
        size="sm"
        :variant="activeCategory === c ? 'default' : 'outline'"
        @click="activeCategory = activeCategory === c ? 'all' : c"
      >
        {{ c }}
      </Button>
    </div>

    <!-- Shimmer skeleton — mirrors the bento grid shape -->
    <div v-if="loading" id="menu-grid" class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4 lg:grid-flow-dense">
      <div class="fu-shimmer aspect-[4/3] rounded-[1.25rem] sm:col-span-2 sm:row-span-2" />
      <div v-for="i in 5" :key="i" class="fu-shimmer aspect-[4/3] rounded-[1.25rem]" />
    </div>

    <!-- Gapless bento grid -->
    <div
      v-else
      id="menu-grid"
      class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4 lg:grid-flow-dense"
    >
      <div
        v-for="(item, i) in filtered"
        :key="item.id"
        :class="`pos-reveal ${revealed ? 'is-visible' : ''} ${cardSpan(i)}`"
        :style="{ transitionDelay: `${Math.min(i * 50, 350)}ms` }"
      >
        <article
          class="group relative flex h-full flex-col overflow-hidden rounded-[1.25rem] border border-border/70 bg-card text-card-foreground shadow-[0_24px_48px_-24px_hsl(var(--pos-ink)/0.12)] transition-all duration-500 ease-[cubic-bezier(0.32,0.72,0,1)] hover:-translate-y-1 hover:shadow-[0_32px_64px_-28px_hsl(var(--pos-ink)/0.24)]"
        >
          <!-- Imagery — Image Scale & Fade target -->
          <div
            data-gsap-media
            class="relative aspect-[4/3] overflow-hidden bg-base-200/70 sm:aspect-[16/10] lg:aspect-auto lg:min-h-[180px] lg:flex-1"
          >
            <img
              v-if="item.image"
              :src="item.image"
              :alt="item.name"
              loading="lazy"
              class="h-full w-full object-cover transition-transform duration-700 ease-out group-hover:scale-105"
            />
            <div
              v-else
              class="flex h-full w-full items-center justify-center bg-gradient-to-br from-base-200 to-base-300/80"
            >
              <span class="font-display text-5xl font-bold text-base-content/15">{{ letterTile(item.name) }}</span>
            </div>
            <div class="absolute inset-0 bg-gradient-to-t from-black/25 to-transparent opacity-0 transition-opacity duration-500 group-hover:opacity-100" />
            <Badge
              v-if="item.category"
              variant="outline"
              class="absolute left-3 top-3 border-white/20 bg-black/30 text-white backdrop-blur-md"
            >
              {{ item.category }}
            </Badge>
          </div>

          <!-- Body -->
          <div class="flex flex-1 flex-col justify-between gap-3 p-4">
            <div class="flex items-start justify-between gap-3">
              <h2 class="font-display text-base font-bold leading-snug tracking-tight">{{ item.name }}</h2>
              <span class="shrink-0 font-mono text-sm font-bold text-primary">{{ money(item.price) }}</span>
            </div>

            <!-- Add / stepper — tactile, springy -->
            <div class="mt-auto">
              <div v-if="qty(item.id) === 0" class="flex justify-end">
                <Button size="sm" class="gap-1.5 px-4" @click="add(item.id)">
                  Add
                  <Plus class="h-3.5 w-3.5" />
                </Button>
              </div>
              <div v-else class="bezel inline-flex items-center gap-1 rounded-full">
                <div class="bezel-core flex items-center gap-1 py-0.5 pl-0.5 pr-1">
                  <Button size="icon" variant="ghost" class="h-7 w-7" @click="remove(item.id)">
                    <Minus class="h-3.5 w-3.5" />
                  </Button>
                  <span class="min-w-6 text-center font-mono text-sm font-bold">{{ qty(item.id) }}</span>
                  <Button size="icon" variant="ghost" class="h-7 w-7" @click="add(item.id)">
                    <Plus class="h-3.5 w-3.5" />
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </article>
      </div>
    </div>

    <!-- Empty states -->
    <div
      v-if="!loading && filtered.length === 0"
      class="bezel pos-reveal"
      :class="revealed ? 'is-visible' : ''"
    >
      <div class="bezel-core px-6 py-16 text-center">
        <p class="eyebrow">{{ query ? 'No match' : 'Quiet kitchen' }}</p>
        <p class="mt-4 text-lg text-base-content/60">
          {{ query ? `Nothing matches “${query}”.` : 'No menu items available' }}
        </p>
        <p class="mt-1 text-sm text-base-content/40">Start the Django portal on :8075 to see items</p>
      </div>
    </div>

    <!-- Floating ticket summary -->
    <Transition
      enter-active-class="transition duration-500 ease-[cubic-bezier(0.32,0.72,0,1)]"
      enter-from-class="translate-y-4 opacity-0"
      enter-to-class="translate-y-0 opacity-100"
      leave-active-class="transition duration-300 ease-[cubic-bezier(0.32,0.72,0,1)]"
      leave-from-class="translate-y-0 opacity-100"
      leave-to-class="translate-y-4 opacity-0"
    >
      <div
        v-if="totalItems > 0 || placedReference"
        class="pos-fade fixed bottom-6 left-1/2 z-30 -translate-x-1/2"
      >
        <div class="bezel shadow-[0_32px_64px_-24px_hsl(var(--pos-ink)/0.35)]">
          <div class="bezel-core flex flex-col gap-3 px-5 py-3">
            <!-- Success: order placed -->
            <div v-if="placedReference" class="flex items-center gap-3">
              <span class="flex h-8 w-8 items-center justify-center rounded-full bg-success/15 text-success">
                <Check class="h-4 w-4" />
              </span>
              <div>
                <p class="text-sm font-semibold">Order placed</p>
                <p class="font-mono text-xs text-muted-foreground">Reference {{ placedReference }}</p>
              </div>
              <Button size="sm" variant="ghost" class="ml-2" @click="placedReference = ''">
                New ticket
              </Button>
            </div>

            <!-- Ticket summary + submit -->
            <template v-else>
              <div class="flex items-center gap-4">
                <span class="font-mono text-[0.65rem] font-semibold uppercase tracking-[0.2em] text-base-content/50">
                  Ticket · {{ totalItems }} item{{ totalItems === 1 ? '' : 's' }}
                </span>
                <span class="stat-value-display text-xl text-primary">{{ money(totalPrice) }}</span>
              </div>

              <div class="flex flex-wrap items-center gap-2">
                <div class="bezel">
                  <div class="bezel-core flex items-center gap-1 py-0.5 pl-0.5 pr-1">
                    <select
                      v-model="orderType"
                      class="bg-transparent py-1 pl-2 pr-6 text-xs font-semibold outline-none"
                      aria-label="Order type"
                    >
                      <option v-for="t in ORDER_TYPES" :key="t.value" :value="t.value">
                        {{ t.label }}
                      </option>
                    </select>
                  </div>
                </div>
                <Button
                  size="sm"
                  class="gap-1.5 px-4"
                  :disabled="submitting"
                  @click="placeOrder"
                >
                  <Loader2 v-if="submitting" class="h-3.5 w-3.5 animate-spin" />
                  {{ submitting ? 'Placing…' : 'Place order' }}
                </Button>
              </div>

              <p v-if="submitError" class="flex items-center gap-1.5 text-xs text-error">
                <X class="h-3.5 w-3.5" />
                {{ submitError }}
              </p>
            </template>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>
