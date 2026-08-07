<script setup lang="ts">
import { ref } from 'vue';
import { useSettingsStore } from '../utils/settings';

const settings = useSettingsStore();
const sidecarUrl = ref(settings.$state.sidecarUrl || 'http://localhost:8765');
const portalUrl = ref(settings.$state.portalUrl || 'http://localhost:8080');

function save() {
  settings.$patch({ sidecarUrl: sidecarUrl.value, portalUrl: portalUrl.value });
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
            <span class="label-text">Sidecar API URL</span>
          </label>
          <input v-model="sidecarUrl" type="text" class="input input-bordered" />
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
