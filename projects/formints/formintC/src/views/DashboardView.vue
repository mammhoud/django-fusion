<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { getHealth, getProducts, getSales, type HealthStatus, type Product, type Sale } from '../api';

const health = ref<HealthStatus | null>(null);
const products = ref<Product[]>([]);
const sales = ref<Sale[]>([]);

onMounted(async () => {
  try {
    health.value = await getHealth();
  } catch {}
  try {
    products.value = await getProducts();
  } catch {}
  try {
    sales.value = await getSales();
  } catch {}
});
</script>

<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-6">POS Dashboard</h1>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
      <div class="stat bg-base-200 rounded-box p-4">
        <div class="stat-title">Products</div>
        <div class="stat-value text-primary">{{ products.length }}</div>
        <div class="stat-desc">From sidecar API</div>
      </div>
      <div class="stat bg-base-200 rounded-box p-4">
        <div class="stat-title">Orders</div>
        <div class="stat-value text-secondary">{{ sales.length }}</div>
        <div class="stat-desc">Recent transactions</div>
      </div>
      <div class="stat bg-base-200 rounded-box p-4">
        <div class="stat-title">Sidecar</div>
        <div class="stat-value" :class="health?.status === 'ok' ? 'text-success' : 'text-error'">
          {{ health?.status === 'ok' ? 'Online' : 'Offline' }}
        </div>
        <div class="stat-desc">{{ health?.service || '—' }}</div>
      </div>
    </div>

    <div class="card bg-base-200 shadow-xl">
      <div class="card-body">
        <h2 class="card-title">Quick Actions</h2>
        <div class="flex flex-wrap gap-2 mt-4">
          <router-link to="/menu" class="btn btn-primary">Browse Menu</router-link>
          <router-link to="/orders" class="btn btn-secondary">View Orders</router-link>
          <router-link to="/settings" class="btn btn-ghost">Settings</router-link>
        </div>
      </div>
    </div>
  </div>
</template>
