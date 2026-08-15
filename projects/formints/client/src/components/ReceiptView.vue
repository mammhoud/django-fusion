<script setup lang="ts">
import { onMounted, onUnmounted, watch } from 'vue';
import Icon from '@/components/ui/Icon.vue';
import type { SaleDetail } from '../api';
import { Button } from '@/components/ui/button';

const props = defineProps<{
  open: boolean;
  sale: SaleDetail | null;
}>();

const emit = defineEmits<{ close: [] }>();

const money = (n: number, currency = '$') => `${currency}${n.toFixed(2)}`;

/** True when running inside the Tauri webview (desktop app). */
const isTauri = typeof window !== 'undefined' && '__TAURI_INTERNALS__' in window;

/**
 * Print through the Tauri native print dialog when running in the desktop
 * app; falls back to the browser print dialog (dev/preview) otherwise. Both
 * paths render the same `@media print` receipt stylesheet.
 */
async function printReceipt() {
  if (isTauri) {
    try {
      const { invoke } = await import('@tauri-apps/api/core');
      await invoke('print_receipt');
      return;
    } catch (err) {
      // Native print unavailable — fall through to the webview dialog.
      console.warn('Native print failed, falling back to window.print()', err);
    }
  }
  window.print();
}

function onKeydown(e: KeyboardEvent) {
  if (!props.open) {
    return;
  }
  if (e.key === 'Escape') {
    emit('close');
    return;
  }
  // Cmd/Ctrl+P → open the receipt print dialog (native in Tauri, browser
  // dialog otherwise). preventDefault stops the webview's own print handling
  // so we always route through printReceipt().
  if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'p') {
    e.preventDefault();
    if (!e.repeat) {
      void printReceipt();
    }
  }
}

watch(
  () => props.open,
  (open) => {
    if (open) {
      window.addEventListener('keydown', onKeydown);
    } else {
      window.removeEventListener('keydown', onKeydown);
    }
  },
);

onMounted(() => {
  if (props.open) {
    window.addEventListener('keydown', onKeydown);
  }
});

onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown);
});
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open && sale"
      class="receipt-overlay fixed inset-0 z-50 overflow-y-auto bg-black/50 p-4 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      :aria-label="`Receipt for order ${sale.reference}`"
      @click.self="emit('close')"
    >
      <!-- Toolbar — screen only, hidden on print -->
      <div
        class="receipt-toolbar mx-auto flex w-[min(88mm,100%)] items-center justify-between gap-3 pb-3"
      >
        <p class="font-mono text-[0.65rem] uppercase tracking-widest text-white/70">
          Receipt · {{ sale.reference }}
          <span class="hidden text-white/40 sm:inline">· Ctrl/⌘ P</span>
        </p>
        <div class="flex items-center gap-2">
          <Button variant="outline" class="h-8 gap-2 border-white/25 bg-white/10 text-white hover:bg-white/20" @click="printReceipt">
            <Icon name="printer" class="h-3.5 w-3.5" />
            Print
          </Button>
          <Button variant="ghost" class="receipt-close h-8 gap-2 text-white hover:bg-white/10" @click="emit('close')">
            <Icon name="x" class="h-3.5 w-3.5" />
            Close
          </Button>
        </div>
      </div>

      <!-- The slip -->
      <div class="receipt-slip mx-auto my-4 rounded-2xl">
        <div class="receipt-pad p-6 font-mono text-[13px] leading-relaxed text-black">
          <!-- Shop header -->
          <div class="text-center">
            <p class="text-[15px] font-bold tracking-tight">FORMINT CAFÉ</p>
            <p class="mt-0.5 text-[10px] uppercase tracking-[0.18em] text-black/50">
              Roasted to order · Brewed to the table
            </p>
          </div>

          <div class="my-3 border-t border-dashed border-black/25" />

          <!-- Order meta -->
          <div class="flex items-center justify-between">
            <span class="font-bold">ORDER #{{ sale.reference }}</span>
            <span class="uppercase tracking-widest text-black/60">{{ sale.status }}</span>
          </div>
          <p class="mt-1 text-[11px] text-black/60">
            {{ sale.date }} · {{ sale.time }}
          </p>
          <p class="mt-1 text-[11px] uppercase tracking-widest text-black/60">
            {{ sale.order_type.replace('_', ' ') }}
          </p>

          <div class="my-3 border-t border-dashed border-black/25" />

          <!-- Customer -->
          <p class="text-[10px] font-bold uppercase tracking-[0.18em] text-black/50">Customer</p>
          <p class="mt-1 font-semibold">{{ sale.customer_name }}</p>
          <p class="text-[11px] text-black/60">{{ sale.customer_email }}</p>
          <p v-if="sale.customer_phone" class="text-[11px] text-black/60">{{ sale.customer_phone }}</p>

          <div class="my-3 border-t border-dashed border-black/25" />

          <!-- Line items -->
          <div class="flex items-baseline justify-between text-[10px] font-bold uppercase tracking-[0.18em] text-black/50">
            <span>Item</span>
            <span>Total</span>
          </div>
          <div class="mt-2 space-y-1.5">
            <div
              v-for="item in sale.items"
              :key="item.id"
              class="flex items-start justify-between gap-3"
            >
              <div class="min-w-0">
                <p class="truncate font-semibold">{{ item.product_name }}</p>
                <p class="text-[11px] text-black/60">{{ item.quantity }} × {{ money(item.price, sale.currency) }}</p>
              </div>
              <span class="shrink-0">{{ money(item.subtotal, sale.currency) }}</span>
            </div>
          </div>

          <div class="my-3 border-t border-dashed border-black/25" />

          <!-- Totals -->
          <div class="space-y-1">
            <div class="flex justify-between text-[12px] text-black/70">
              <span>Subtotal</span>
              <span>{{ money(sale.subtotal, sale.currency) }}</span>
            </div>
            <div class="flex justify-between text-[12px] text-black/70">
              <span>Tax</span>
              <span>{{ money(sale.tax, sale.currency) }}</span>
            </div>
            <div class="mt-1 flex justify-between border-t border-black/30 pt-1 text-[15px] font-bold">
              <span>TOTAL</span>
              <span>{{ money(sale.total_amount, sale.currency) }}</span>
            </div>
          </div>

          <!-- Notes -->
          <template v-if="sale.notes">
            <div class="my-3 border-t border-dashed border-black/25" />
            <p class="text-[10px] font-bold uppercase tracking-[0.18em] text-black/50">Notes</p>
            <p class="mt-1 text-[11px] text-black/70">{{ sale.notes }}</p>
          </template>

          <!-- Footer -->
          <div class="my-3 border-t border-dashed border-black/25" />
          <div class="text-center">
            <p class="text-[11px] font-semibold">Thank you — see you soon!</p>
            <p class="mt-0.5 text-[10px] uppercase tracking-[0.18em] text-black/50">
              #{{ sale.reference }} · {{ sale.date }} {{ sale.time }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>
