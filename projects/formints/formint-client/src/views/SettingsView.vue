<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useSettingsStore, type AppLocale } from '../utils/settings';
import { useLanguage, SUPPORTED_LOCALES } from '../utils/i18n';
import { getClientVersion } from '../utils/version';
import {
  getFusionAssets,
  getFusionRenderMode,
  getFusionSessionMode,
  setFusionSessionMode,
  clearFusionSessionMode,
  type FusionAssets,
  type FusionRenderMode,
  type FusionSessionMode,
} from '../api';
import { CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Switch } from '@/components/ui/switch';

const settings = useSettingsStore();
const portalUrl = ref(settings.portalUrl);
const { switchLanguage, t } = useLanguage();
const language = ref<AppLocale>(settings.language);

async function onLanguageChange(event: Event) {
  const value = (event.target as HTMLSelectElement).value as AppLocale;
  language.value = value;
  await switchLanguage(value);
}
const revealed = ref(false);

// ── Version + fusion status ────────────────────────────────────────────
const clientVersion = ref('…');
const fusionAssets = ref<FusionAssets | null>(null);
const renderMode = ref<FusionRenderMode | null>(null);
const sessionMode = ref<FusionSessionMode | null>(null);
const sessionPreference = ref(false);
const fusionError = ref('');
const busy = ref(false);

onMounted(async () => {
  requestAnimationFrame(() => {
    revealed.value = true;
  });

  // Client version — was empty before because nothing fetched it.
  getClientVersion().then((v) => (clientVersion.value = v));

  // Fusion contract — version hash + render mode + session preference.
  try {
    fusionAssets.value = await getFusionAssets();
  } catch {
    fusionError.value = 'Backend offline — start the Django portal on :8075.';
  }
  try {
    renderMode.value = await getFusionRenderMode();
  } catch {
    /* surfaced above */
  }
  try {
    sessionMode.value = await getFusionSessionMode();
    sessionPreference.value = sessionMode.value.session_preference ?? sessionMode.value.default;
  } catch {
    /* surfaced above */
  }
});

function save() {
  void settings.updateAndSaveSettings({
    portalUrl: portalUrl.value,
  });
}

async function onToggleSessionMode(value: boolean) {
  busy.value = true;
  try {
    sessionMode.value = await setFusionSessionMode(value);
    sessionPreference.value = value;
  } catch {
    sessionPreference.value = !value;
  } finally {
    busy.value = false;
  }
}

async function onClearSessionMode() {
  busy.value = true;
  try {
    sessionMode.value = await clearFusionSessionMode();
    sessionPreference.value = sessionMode.value.default;
  } finally {
    busy.value = false;
  }
}
</script>

<template>
  <div class="space-y-8">
    <div class="pos-reveal" :class="revealed ? 'is-visible' : ''">
      <p class="eyebrow">Preferences</p>
      <h1 class="mt-3 text-3xl font-bold tracking-tight">Settings</h1>
      <p class="mt-1 text-sm text-base-content/50">Connection, fusion mode, and client identity.</p>
    </div>

    <!-- Connection -->
    <div class="bezel pos-reveal max-w-xl" :class="revealed ? 'is-visible' : ''" style="transition-delay: 90ms">
      <div class="bezel-core p-6 sm:p-7">
        <CardHeader class="p-0">
          <CardTitle>Connection</CardTitle>
          <CardDescription>Endpoints the POS client talks to.</CardDescription>
        </CardHeader>          <div class="mt-5 space-y-4">
            <div>
              <label class="label pb-1.5">
                <span class="font-mono text-[0.65rem] font-semibold uppercase tracking-widest text-base-content/50">
                  Backend API URL (Django portal)
                </span>
              </label>
              <Input v-model="portalUrl" type="text" class="bg-background" />
            </div>
          </div>

        <div class="mt-7 flex justify-end">
          <Button @click="save">Save</Button>
        </div>
      </div>
    </div>

    <!-- Language -->
    <div class="bezel pos-reveal max-w-xl" :class="revealed ? 'is-visible' : ''" style="transition-delay: 140ms">
      <div class="bezel-core p-6 sm:p-7">
        <CardHeader class="p-0">
          <CardTitle>{{ t('settings.language') }}</CardTitle>
          <CardDescription>{{ t('settings.selectLanguage') }}</CardDescription>
        </CardHeader>

        <div class="mt-5">
          <select
            :value="language"
            @change="onLanguageChange"
            class="select select-sm select-bordered w-full max-w-xs bg-background font-medium"
            aria-label="Language"
          >
            <option v-for="loc in SUPPORTED_LOCALES" :key="loc" :value="loc">
              {{ t(`settings.languages.${loc}`) }}
            </option>
          </select>
          <p class="mt-3 text-xs text-muted-foreground">{{ t('settings.autoSave') }}</p>
        </div>
      </div>
    </div>

    <!-- Fusion render mode (django-fusion contract) -->
    <div class="bezel pos-reveal max-w-xl" :class="revealed ? 'is-visible' : ''" style="transition-delay: 180ms">
      <div class="bezel-core p-6 sm:p-7">
        <CardHeader class="p-0">
          <CardTitle class="flex items-center gap-3">
            Fusion render mode
            <Badge
              v-if="renderMode"
              :variant="renderMode.fusion_render_first ? 'success' : 'outline'"
            >
              {{ renderMode.mode }}
            </Badge>
          </CardTitle>
          <CardDescription>
            django-fusion dual-mode contract — server-rendered HTML vs data APIs.
          </CardDescription>
        </CardHeader>

        <p v-if="fusionError" class="mt-4 rounded-xl border border-error/20 bg-error/5 px-4 py-3 text-sm text-error">
          {{ fusionError }}
        </p>

        <template v-else>
          <div class="mt-5 space-y-4">
            <div class="flex items-center justify-between gap-4">
              <div>
                <p class="text-sm font-semibold">Session preference</p>
                <p class="text-xs text-muted-foreground">
                  {{ sessionPreference ? 'Render-first (finished HTML)' : 'Data APIs (JSON + fragments)' }}
                </p>
              </div>
              <Switch :disabled="busy" :model-value="sessionPreference" @update:model-value="onToggleSessionMode" />
            </div>
            <Separator />
            <div class="flex items-center justify-between gap-4">
              <div>
                <p class="text-sm font-semibold">Backend assets</p>
                <p class="font-mono text-xs text-muted-foreground">Fusion asset manifest</p>
              </div>
              <Badge variant="outline">{{ fusionAssets?.version ? `v${fusionAssets.version}` : '—' }}</Badge>
            </div>
          </div>

          <div class="mt-6 flex justify-end">
            <Button variant="ghost" size="sm" :disabled="busy || !sessionMode?.session_cached" @click="onClearSessionMode">
              Clear preference
            </Button>
          </div>
        </template>
      </div>
    </div>

    <!-- About — the client version (was empty: nothing fetched it) -->
    <div class="bezel pos-reveal max-w-xl" :class="revealed ? 'is-visible' : ''" style="transition-delay: 270ms">
      <div class="bezel-core p-6 sm:p-7">
        <CardHeader class="p-0">
          <CardTitle>About</CardTitle>
          <CardDescription>Client + backend identity.</CardDescription>
        </CardHeader>

        <div class="mt-5 space-y-3">
          <div class="flex items-center justify-between gap-4">
            <span class="text-sm text-muted-foreground">Client version</span>
            <Badge variant="secondary">{{ clientVersion }}</Badge>
          </div>
          <Separator />
          <div class="flex items-center justify-between gap-4">
            <span class="text-sm text-muted-foreground">Backend fusion version</span>
            <Badge variant="outline">{{ fusionAssets?.version ? `v${fusionAssets.version}` : '—' }}</Badge>
          </div>
          <Separator />
          <div class="flex items-center justify-between gap-4">
            <span class="text-sm text-muted-foreground">Product</span>
            <span class="font-mono text-xs font-semibold">Formint Client · Tauri + Vue 3</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
