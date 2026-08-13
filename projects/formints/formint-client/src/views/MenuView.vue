<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { getProducts, type Product } from '../api';

const items = ref<Product[]>([]);
const loading = ref(true);

onMounted(async () => {
  try {
    items.value = await getProducts();
  } catch {}
  loading.value = false;
});
</script>

<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-6">Menu</h1>

    <div v-if="loading" class="flex justify-center">
      <span class="loading loading-spinner loading-lg"></span>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="item in items" :key="item.id" class="card bg-base-200 shadow-xl hover:shadow-2xl transition-shadow">
        <div class="card-body">
          <h2 class="card-title mt-2">{{ item.name }}</h2>
          <div class="card-actions justify-end items-center mt-4">
            <span class="text-lg font-bold">${{ item.price }}</span>
            <button class="btn btn-primary btn-sm">Add to Order</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="!loading && items.length === 0" class="text-center py-12">
      <p class="text-lg opacity-60">No menu items available</p>
      <p class="text-sm opacity-40 mt-2">Connect to the POS sidecar to see items</p>
    </div>
  </div>
</template>
