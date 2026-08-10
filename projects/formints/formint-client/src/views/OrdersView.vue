<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { getSales, type Sale } from '../api';

const sales = ref<Sale[]>([]);
const loading = ref(true);

onMounted(async () => {
  try {
    sales.value = await getSales();
  } catch {}
  loading.value = false;
});
</script>

<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-6">Orders</h1>

    <div v-if="loading" class="flex justify-center">
      <span class="loading loading-spinner loading-lg"></span>
    </div>

    <div v-else class="space-y-4">
      <div v-for="sale in sales" :key="sale.id" class="card bg-base-200 shadow-xl">
        <div class="card-body">
          <div class="flex justify-between items-start">
            <div>
              <h2 class="card-title">Order #{{ sale.id }}</h2>
              <p class="text-sm opacity-60">{{ sale.date }} {{ sale.time }}</p>
            </div>
            <div class="text-right">
              <div class="badge" :class="sale.status === 'completed' ? 'badge-success' : 'badge-warning'">
                {{ sale.status }}
              </div>
              <p class="text-lg font-bold mt-1">{{ sale.currency }} {{ sale.total_amount }}</p>
            </div>
          </div>
          <div v-if="sale.items?.length" class="mt-4">
            <p class="text-sm font-semibold mb-2">Items ({{ sale.items.length }})</p>
            <div v-for="item in sale.items" :key="item.id" class="flex justify-between text-sm py-1">
              <span>{{ item.product_name }} × {{ item.quantity }}</span>
              <span>{{ sale.currency }} {{ item.subtotal }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="!loading && sales.length === 0" class="text-center py-12">
      <p class="text-lg opacity-60">No orders yet</p>
    </div>
  </div>
</template>
