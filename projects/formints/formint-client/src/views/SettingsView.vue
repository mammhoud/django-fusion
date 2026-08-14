<script setup lang="ts">
import { ref } from 'vue';
import { useSettingsStore } from '../utils/settings';

// Env-driven defaults (Vite .env); user-configured settings still win.
const ENV_SERVER_URL = (import.meta.env?.VITE_SERVER_URL as string | undefined) || 'http://localhost:8765';
const ENV_PORTAL_URL = (import.meta.env?.VITE_PORTAL_URL as string | undefined) || 'http://localhost:8080';

const settings = useSettingsStore();
const serverUrl = ref(settings.$state.serverUrl || ENV_SERVER_URL);
const portalUrl = ref(settings.$state.portalUrl || ENV_PORTAL_URL);

function save() {
  settings.$patch({ serverUrl: serverUrl.value, portalUrl: portalUrl.value });
}
</script>

<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-6">Settings</h1>

    <div class="card bg-base-200 shadow-xl max-w-md">
      <div class="card-body">
        <h2 class="card-title">Connection</h2>

        <div class="form-control mt-4">
          <label class="label">
            <span class="label-text">Server API URL</span>
          </label>
          <input v-model="serverUrl" type="text" class="input input-bordered" />
        </div>

        <div class="form-control mt-2">
          <label class="label">
            <span class="label-text">Portal Django URL</span>
          </label>
          <input v-model="portalUrl" type="text" class="input input-bordered" />
        </div>

        <div class="card-actions justify-end mt-6">
          <button @click="save" class="btn btn-primary">Save</button>
        </div>
      </div>
    </div>
  </div>
</template>
