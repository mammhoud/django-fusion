<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { ChevronDown, ChevronsUpDown, Printer, CookingPot, Check } from 'lucide-vue-next';
import { getSales, getSale, updateOrderStatus, type Sale, type SaleDetail } from '../api';
import { useOrdersStore } from '@/utils/orders';
import { useTicketStore } from '@/utils/ticket';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import ReceiptView from '@/components/ReceiptView.vue';

/** Expanded-orders state + detail cache + status filter live in the store,
 *  so they survive navigating away from this view and back. */
const ordersStore = useOrdersStore();

/** Ticket store — its dataVersion bumps when a new order is placed, so a
 *  mounted Orders view refetches instead of staying stale. */
const ticketStore = useTicketStore();

const sales = ref<Sale[]>([]);
const loading = ref(true);
const revealed = ref(false);

/** Canonical order-status display order (mirrors backend Order.Status). */
const STATUS_ORDER = ['pending', 'confirmed', 'preparing', 'ready', 'completed', 'cancelled'];

/** Distinct statuses present in the loaded orders, each with a live count. */
const statusCounts = computed(() => {
  const counts = new Map<string, number>();
  for (const s of sales.value) {
    counts.set(s.status, (counts.get(s.status) ?? 0) + 1);
  }
  const known = STATUS_ORDER.filter((st) => counts.has(st)).map((st) => ({
    status: st,
    count: counts.get(st) ?? 0,
  }));
  // Unknown statuses (added on the backend later) still get a filter chip.
  const unknown = [...counts.keys()]
    .filter((st) => !STATUS_ORDER.includes(st))
    .map((st) => ({ status: st, count: counts.get(st) ?? 0 }));
  return [...known, ...unknown];
});

/** Humanize an order-status key: preparing → Preparing, dine_in → Dine In. */
const formatStatus = (status: string) =>
  status.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());

/** Fulfilment chain — the kitchen advances one step at a time.
 *  Confirmed is a backend-only state not used in the POS flow, so the
 *  UI advances pending → preparing → ready → completed. */
const STATUS_CHAIN = ['pending', 'preparing', 'ready', 'completed'];

/** Next step in the chain, or null when the order is terminal/complete. */
function nextStep(status: string): { status: string; label: string } | null {
  const i = STATUS_CHAIN.indexOf(status);
  if (i < 0 || i >= STATUS_CHAIN.length - 1) {
    return null;
  }
  const next = STATUS_CHAIN[i + 1];
  const labels: Record<string, string> = {
    preparing: 'Start preparing',
    ready: 'Mark ready',
    completed: 'Complete',
  };
  return { status: next, label: labels[next] ?? next };
}

const advancingId = ref<number | null>(null);

/** Advance one order a step; on success update the card + cached detail in place. */
async function advanceStatus(sale: Sale) {
  const step = nextStep(sale.status);
  if (!step || advancingId.value !== null) {
    return;
  }
  advancingId.value = sale.id;
  try {
    const updated = await updateOrderStatus(sale.id, step.status);
    const idx = sales.value.findIndex((s) => s.id === sale.id);
    if (idx !== -1) {
      sales.value = sales.value.map((s) => (s.id === sale.id ? updated : s));
    }
    // Keep the cached detail fresh so an open expansion matches.
    ordersStore.setDetail(updated);
    // A completed order may vanish from the active filter — prune leftovers.
    ordersStore.prune(sales.value.map((s) => s.id));
  } catch {
    // Leave the card as-is; the badge still reflects the server's state.
  } finally {
    advancingId.value = null;
  }
}

/** Orders visible under the active status filter. */
const filteredSales = computed(() =>
  ordersStore.statusFilter === 'all'
    ? sales.value
    : sales.value.filter((s) => s.status === ordersStore.statusFilter),
);

const detailLoading = ref(false);
const expandingAll = ref(false);

const receiptSale = ref<SaleDetail | null>(null);
const receiptLoading = ref(false);

const allExpanded = computed(
  () =>
    filteredSales.value.length > 0 &&
    filteredSales.value.every((s) => ordersStore.expandedIds.includes(s.id)),
);

function isExpanded(id: number) {
  return ordersStore.expandedIds.includes(id);
}

/** Fetch the order list, pruning expanded ids that no longer exist. */
async function loadSales() {
  try {
    sales.value = await getSales();
    ordersStore.prune(sales.value.map((s) => s.id));
  } catch {}
}

onMounted(async () => {
  requestAnimationFrame(() => {
    revealed.value = true;
  });
  await loadSales();
  loading.value = false;
});

// Refetch whenever a new order is placed (signal bumped by MenuView's ticket).
watch(
  () => ticketStore.dataVersion,
  () => {
    loadSales();
  },
);

const statusVariant = (status: string) =>
  status === 'completed' || status === 'ready'
    ? ('success' as const)
    : status === 'cancelled'
      ? ('destructive' as const)
      : ('warning' as const);

/** Tailwind text-color class per status — tints the filter-chip dots. */
const statusTextClass = (status: string) =>
  status === 'completed' || status === 'ready'
    ? 'text-success'
    : status === 'cancelled'
      ? 'text-destructive'
      : 'text-warning';

const money = (n: number) => `$${n.toFixed(2)}`;

async function toggleExpand(sale: Sale) {
  const wasExpanded = ordersStore.expandedIds.includes(sale.id);
  ordersStore.toggle(sale.id);
  if (!wasExpanded) {
    await ensureDetail(sale);
  }
}

/** Fetch + cache one order's full detail unless already cached (in the store). */
async function ensureDetail(sale: Sale) {
  if (ordersStore.details[sale.id]) {
    return;
  }
  detailLoading.value = true;
  try {
    ordersStore.setDetail(await getSale(sale.id));
  } catch {
    ordersStore.markFailed(sale.id);
  } finally {
    detailLoading.value = false;
  }
}

/** Expand every visible order (fetching all details in parallel) or collapse all. */
async function toggleExpandAll() {
  if (allExpanded.value) {
    ordersStore.collapseAll();
    return;
  }
  if (expandingAll.value) {
    return;
  }
  expandingAll.value = true;
  try {
    ordersStore.expandAll(filteredSales.value.map((s) => s.id));
    const pending = filteredSales.value.filter((s) => !ordersStore.details[s.id]);
    if (pending.length > 0) {
      await Promise.allSettled(pending.map((s) => ensureDetail(s)));
    }
  } finally {
    expandingAll.value = false;
  }
}

/** Open the printable receipt — reuses the cached detail or fetches it. */
async function openReceipt(sale: Sale) {
  if (ordersStore.details[sale.id]) {
    receiptSale.value = ordersStore.details[sale.id];
    return;
  }
  receiptLoading.value = true;
  try {
    receiptSale.value = await getSale(sale.id);
  } catch {
    receiptSale.value = {
      ...sale,
      customer_name: '',
      customer_email: '',
      customer_phone: '',
      notes: '',
      subtotal: sale.total_amount,
      discount: 0,
      tax: 0,
      payment_method: 'cash',
      promo_code: '',
      ready_at: null,
      table_number: '',
      delivery_address: '',
      delivery_city: '',
      delivery_zip: '',
    };
  } finally {
    receiptLoading.value = false;
  }
}
</script>

<template>
  <div class="space-y-8">
    <div
      class="pos-reveal flex flex-wrap items-end justify-between gap-4"
      :class="revealed ? 'is-visible' : ''"
    >
      <div>
        <p class="eyebrow">Ledger</p>
        <h1 class="mt-3 text-3xl font-bold tracking-tight">Orders</h1>
        <p class="mt-1 text-sm text-base-content/50">
          Tap an order to expand its full detail — or expand them all at once.
        </p>
      </div>
      <Button
        v-if="!loading && filteredSales.length > 0"
        variant="outline"
        class="gap-2"
        @click="toggleExpandAll"
      >
        <ChevronsUpDown class="h-4 w-4" />
        {{ allExpanded ? 'Collapse all' : `Expand all (${filteredSales.length})` }}
      </Button>
    </div>

    <!-- Status filter bar -->
    <div
      v-if="!loading && statusCounts.length > 0"
      class="pos-reveal flex flex-wrap items-center gap-2"
      :class="revealed ? 'is-visible' : ''"
    >
      <Button
        size="sm"
        :variant="ordersStore.statusFilter === 'all' ? 'default' : 'outline'"
        @click="ordersStore.setStatusFilter('all')"
      >
        All
        <span class="rounded-full bg-black/10 px-1.5 font-mono text-[0.65rem] dark:bg-white/15">
          {{ sales.length }}
        </span>
      </Button>
      <Button
        v-for="entry in statusCounts"
        :key="entry.status"
        size="sm"
        :variant="ordersStore.statusFilter === entry.status ? 'default' : 'outline'"
        class="capitalize"
        @click="ordersStore.setStatusFilter(ordersStore.statusFilter === entry.status ? 'all' : entry.status)"
      >
        <span class="h-1.5 w-1.5 rounded-full bg-current" :class="statusTextClass(entry.status)" />
        {{ entry.status.replace('_', ' ') }}
        <span class="rounded-full bg-black/10 px-1.5 font-mono text-[0.65rem] dark:bg-white/15">
          {{ entry.count }}
        </span>
      </Button>
    </div>

    <div v-if="loading" class="space-y-5">
      <Skeleton v-for="i in 3" :key="i" class="h-36" />
    </div>

    <div v-else class="space-y-5">
      <Card
        v-for="(sale, i) in filteredSales"
        :key="sale.id"
        :class="`pos-reveal transition-transform duration-500 ease-[cubic-bezier(0.32,0.72,0,1)] ${revealed ? 'is-visible' : ''} ${isExpanded(sale.id) ? 'shadow-[0_28px_56px_-28px_hsl(var(--pos-ink)/0.2)]' : 'hover:-translate-y-0.5'}`"
        :style="{ transitionDelay: `${Math.min(i * 60, 360)}ms` }"
      >
        <CardContent class="p-6">
          <!-- Header row — always visible, toggles expansion -->
          <button
            type="button"
            class="flex w-full items-start justify-between gap-4 text-left"
            @click="toggleExpand(sale)"
            :aria-expanded="isExpanded(sale.id)"
          >
            <div>
              <div class="flex items-center gap-2">
                <h2 class="font-display text-lg font-bold tracking-tight">Order #{{ sale.reference }}</h2>
                <Badge variant="outline">{{ sale.order_type.replace('_', ' ') }}</Badge>
              </div>
              <p class="mt-0.5 font-mono text-xs text-muted-foreground">{{ sale.date }} · {{ sale.time }}</p>
            </div>
            <div class="flex items-center gap-3">
              <div class="text-right">
                <Badge :variant="statusVariant(sale.status)">{{ sale.status }}</Badge>
                <p class="stat-value-display mt-2 text-xl">{{ money(sale.total_amount) }}</p>
              </div>
              <ChevronDown
                class="h-5 w-5 shrink-0 text-muted-foreground transition-transform duration-300 ease-[cubic-bezier(0.32,0.72,0,1)]"
                :class="isExpanded(sale.id) ? 'rotate-180' : ''"
              />
            </div>
          </button>

          <!-- Kitchen actions — advance one step at a time -->
          <div v-if="nextStep(sale.status)" class="mt-4 flex items-center justify-between gap-3 border-t border-border/40 pt-3">
            <p class="font-mono text-[0.65rem] uppercase tracking-widest text-muted-foreground">
              Next: {{ formatStatus(nextStep(sale.status)!.status) }}
            </p>
            <Button
              size="sm"
              :disabled="advancingId !== null"
              @click="advanceStatus(sale)"
            >
              <CookingPot
                v-if="nextStep(sale.status)!.status === 'preparing'"
                class="h-3.5 w-3.5"
              />
              <Check v-else class="h-3.5 w-3.5" />
              {{ advancingId === sale.id ? 'Updating…' : nextStep(sale.status)!.label }}
            </Button>
          </div>

          <!-- Expanded detail — lazy-fetched from GET /api/orders/<id>/ -->
          <div v-if="isExpanded(sale.id)" class="mt-5 border-t border-border/60 pt-5">
            <div
              v-if="detailLoading && !ordersStore.details[sale.id] && !ordersStore.failedIds.includes(sale.id)"
              class="space-y-3"
            >
              <Skeleton v-for="j in 3" :key="j" class="h-6" />
            </div>

            <div v-else-if="ordersStore.failedIds.includes(sale.id)" class="text-sm text-error">
              Couldn't load order detail — showing the summary from the list.
            </div>

            <template v-else>
              <dl
                v-if="ordersStore.details[sale.id]"
                class="grid grid-cols-2 gap-x-6 gap-y-3 sm:grid-cols-4"
              >
                <div>
                  <dt class="font-mono text-[0.65rem] uppercase tracking-widest text-muted-foreground">Customer</dt>
                  <dd class="mt-1 text-sm font-semibold">{{ ordersStore.details[sale.id].customer_name }}</dd>
                  <dd class="text-xs text-muted-foreground">{{ ordersStore.details[sale.id].customer_email }}</dd>
                  <dd v-if="ordersStore.details[sale.id].customer_phone" class="text-xs text-muted-foreground">
                    {{ ordersStore.details[sale.id].customer_phone }}
                  </dd>
                </div>
                <div>
                  <dt class="font-mono text-[0.65rem] uppercase tracking-widest text-muted-foreground">Reference</dt>
                  <dd class="mt-1 font-mono text-sm font-semibold">{{ ordersStore.details[sale.id].reference }}</dd>
                  <dd class="text-xs text-muted-foreground">Placed {{ ordersStore.details[sale.id].date }} {{ ordersStore.details[sale.id].time }}</dd>
                </div>
                <div>
                  <dt class="font-mono text-[0.65rem] uppercase tracking-widest text-muted-foreground">Order type</dt>
                  <dd class="mt-1 text-sm font-semibold capitalize">{{ ordersStore.details[sale.id].order_type.replace('_', ' ') }}</dd>
                </div>
                <div>
                  <dt class="font-mono text-[0.65rem] uppercase tracking-widest text-muted-foreground">Status</dt>
                  <dd class="mt-1">
                    <Badge :variant="statusVariant(ordersStore.details[sale.id].status)">{{ ordersStore.details[sale.id].status }}</Badge>
                  </dd>
                </div>
              </dl>

              <div v-if="ordersStore.details[sale.id]?.notes" class="mt-4 rounded-xl border border-border/60 bg-base-200/40 px-4 py-3 text-sm text-muted-foreground">
                “{{ ordersStore.details[sale.id].notes }}”
              </div>

              <!-- Line items -->
              <div class="mt-5">
                <p class="font-mono text-[0.65rem] font-semibold uppercase tracking-widest text-muted-foreground">
                  Items ({{ ordersStore.details[sale.id]?.items.length || sale.items.length }})
                </p>
                <div class="mt-2 divide-y divide-border/50">
                  <div
                    v-for="item in ordersStore.details[sale.id]?.items || sale.items"
                    :key="item.id"
                    class="flex items-center justify-between gap-4 py-2 text-sm"
                  >
                    <span class="text-muted-foreground">
                      {{ item.product_name }}
                      <span class="font-mono text-xs text-muted-foreground/70">× {{ item.quantity }} @ {{ money(item.price) }}</span>
                    </span>
                    <span class="font-mono text-foreground/80">{{ money(item.subtotal) }}</span>
                  </div>
                </div>
              </div>

              <!-- Totals summary -->
              <div
                v-if="ordersStore.details[sale.id]"
                class="mt-4 flex flex-col items-end gap-1 text-sm"
              >
                <div class="flex w-full max-w-[220px] justify-between text-muted-foreground">
                  <span>Subtotal</span>
                  <span class="font-mono">{{ money(ordersStore.details[sale.id].subtotal) }}</span>
                </div>
                <div class="flex w-full max-w-[220px] justify-between text-muted-foreground">
                  <span>Tax</span>
                  <span class="font-mono">{{ money(ordersStore.details[sale.id].tax) }}</span>
                </div>
                <div class="flex w-full max-w-[220px] justify-between border-t border-border/60 pt-1 font-semibold text-foreground">
                  <span>Total</span>
                  <span class="font-mono">{{ money(ordersStore.details[sale.id].total_amount) }}</span>
                </div>
              </div>

              <!-- Printable receipt -->
              <div class="mt-5 flex justify-end border-t border-border/60 pt-4">
                <Button
                  variant="outline"
                  class="gap-2"
                  :disabled="receiptLoading"
                  @click="openReceipt(sale)"
                >
                  <Printer class="h-4 w-4" />
                  {{ receiptLoading ? 'Preparing…' : 'Print receipt' }}
                </Button>
              </div>
            </template>
          </div>
        </CardContent>
      </Card>
    </div>

    <div v-if="!loading && sales.length === 0" class="bezel pos-reveal" :class="revealed ? 'is-visible' : ''">
      <div class="bezel-core px-6 py-16 text-center">
        <p class="eyebrow">Quiet shift</p>
        <p class="mt-4 text-lg text-base-content/60">No orders yet</p>
      </div>
    </div>

    <div
      v-else-if="!loading && filteredSales.length === 0"
      class="bezel pos-reveal"
      :class="revealed ? 'is-visible' : ''"
    >
      <div class="bezel-core px-6 py-16 text-center">
        <p class="eyebrow">Filtered</p>
        <p class="mt-4 text-lg text-base-content/60">
          No orders with status “{{ formatStatus(ordersStore.statusFilter) }}” yet.
        </p>
        <Button variant="outline" size="sm" class="mt-4" @click="ordersStore.setStatusFilter('all')">
          Clear filter
        </Button>
      </div>
    </div>

    <ReceiptView :open="!!receiptSale" :sale="receiptSale" @close="receiptSale = null" />
  </div>
</template>
