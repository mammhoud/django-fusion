<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { getHealth, getProducts, getSales, type HealthStatus, type Product, type Sale } from '../api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';

const health = ref<HealthStatus | null>(null);
const products = ref<Product[]>([]);
const sales = ref<Sale[]>([]);
const loading = ref(true);
const revealed = ref(false);

onMounted(async () => {
  // Reveal animation after first paint.
  requestAnimationFrame(() => {
    revealed.value = true;
  });
  try {
    health.value = await getHealth();
  } catch {}
  try {
    products.value = await getProducts();
  } catch {}
  try {
    sales.value = await getSales();
  } catch {}
  loading.value = false;
});

const backendOk = () => health.value?.status === 'ok';
</script>

<template>
  <div class="space-y-8">
    <div class="pos-reveal" :class="revealed ? 'is-visible' : ''">
      <p class="eyebrow">Overview</p>
      <h1 class="mt-3 text-3xl font-bold tracking-tight">Formint Client Dashboard</h1>
      <p class="mt-1 text-sm text-base-content/50">The register at a glance — menu, orders, and backend health.</p>
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
          <p v-else class="stat-value-display text-5xl">{{ products.length }}</p>
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
          <p v-else class="stat-value-display text-5xl">{{ sales.length }}</p>
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
          <p v-else class="stat-value-display text-5xl" :class="backendOk() ? 'text-success' : 'text-error'">
            {{ backendOk() ? 'OK' : 'OFF' }}
          </p>
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
  </div>
</template>
