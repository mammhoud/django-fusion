<script setup lang="ts">
import TitleBar from '../components/TitleBar.vue';
import { RouterLink, useRoute } from 'vue-router';

const route = useRoute();

const nav = [
  { to: '/', label: 'Dashboard', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
  { to: '/menu', label: 'Menu', icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2' },
  { to: '/orders', label: 'Orders', icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4' },
  { to: '/settings', label: 'Settings', icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z' },
];
</script>

<template>
  <div class="flex min-h-[100dvh] flex-col bg-base-100">
    <TitleBar />
    <div class="mx-auto flex w-full max-w-[1280px] flex-1 gap-6 px-4 pb-8 pt-4">
      <!-- Floating sidebar — bezel shell + core -->
      <aside class="bezel sticky top-24 hidden w-64 shrink-0 self-start md:block">
        <div class="bezel-core p-3">
          <nav class="space-y-1.5">
            <RouterLink
              v-for="item in nav"
              :key="item.to"
              :to="item.to"
              class="group flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition-all duration-500 ease-[cubic-bezier(0.32,0.72,0,1)]"
              :class="route.path === item.to
                ? 'bg-base-300/70 text-base-content shadow-[inset_0_1px_0_hsl(0_0%_100%/0.5)]'
                : 'text-base-content/60 hover:bg-base-200/70 hover:text-base-content'"
            >
              <span
                class="flex h-8 w-8 items-center justify-center rounded-xl transition-all duration-500 ease-[cubic-bezier(0.32,0.72,0,1)]"
                :class="route.path === item.to
                  ? 'bg-base-content text-base-100'
                  : 'bg-base-200 text-base-content/60 group-hover:scale-105'"
              >
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" :d="item.icon" />
                </svg>
              </span>
              {{ item.label }}
            </RouterLink>
          </nav>
        </div>
      </aside>

      <main class="min-w-0 flex-1">
        <RouterView v-slot="{ Component }">
          <Transition
            mode="out-in"
            enter-active-class="route-enter-active"
            leave-active-class="route-leave-active"
            enter-from-class="route-enter-from"
            leave-to-class="route-leave-to"
          >
            <component :is="Component" />
          </Transition>
        </RouterView>
      </main>
    </div>
  </div>
</template>
