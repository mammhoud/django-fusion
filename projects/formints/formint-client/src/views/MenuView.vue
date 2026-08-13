<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { Plus } from 'lucide-vue-next';
import { getProducts, type Product } from '../api';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';

const items = ref<Product[]>([]);
const loading = ref(true);
const revealed = ref(false);

onMounted(async () => {
  requestAnimationFrame(() => {
    revealed.value = true;
  });
  try {
    items.value = await getProducts();
  } catch {}
  loading.value = false;
});
</script>

<template>
  <div class="space-y-8">
    <div class="pos-reveal" :class="revealed ? 'is-visible' : ''">
      <p class="eyebrow">Catalog</p>
      <h1 class="mt-3 text-3xl font-bold tracking-tight">Menu</h1>
    </div>

    <div v-if="loading" class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
      <Skeleton v-for="i in 6" :key="i" class="h-40" />
    </div>

    <div v-else class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
      <Card
        v-for="(item, i) in items"
        :key="item.id"
        class="pos-reveal transition-transform duration-500 ease-[cubic-bezier(0.32,0.72,0,1)] hover:-translate-y-1 hover:shadow-[0_28px_56px_-28px_hsl(var(--pos-ink)/0.2)]"
        :class="revealed ? 'is-visible' : ''"
        :style="{ transitionDelay: `${Math.min(i * 60, 360)}ms` }"
      >
        <CardContent class="p-5">
          <div class="flex items-center justify-between gap-3">
            <h2 class="font-display text-lg font-bold tracking-tight">{{ item.name }}</h2>
            <Badge variant="secondary">{{ item.unit }}</Badge>
          </div>
          <div class="mt-4 flex items-center justify-between">
            <span class="font-mono text-lg font-bold">${{ item.price }}</span>
            <Button size="sm" variant="outline">
              Add to Order
              <Plus />
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>

    <div v-if="!loading && items.length === 0" class="bezel pos-reveal" :class="revealed ? 'is-visible' : ''">
      <div class="bezel-core px-6 py-16 text-center">
        <p class="eyebrow">Empty</p>
        <p class="mt-4 text-lg text-base-content/60">No menu items available</p>
        <p class="mt-1 text-sm text-base-content/40">Start the Django portal on :8075 to see items</p>
      </div>
    </div>
  </div>
</template>
