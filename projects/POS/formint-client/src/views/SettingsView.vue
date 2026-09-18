<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useSettingsStore, type AppLocale } from '../utils/settings';
import { useLanguage, SUPPORTED_LOCALES } from '../utils/i18n';
import { getClientVersion } from '../utils/version';
import {
  getFusionAssets,
  getFusionEditorial,
  getFusionRenderMode,
  getFusionSessionMode,
  setFusionSessionMode,
  clearFusionSessionMode,
  type EditorialCraft,
  type EditorialVoice,
  type FusionAssets,
  type FusionEditorial,
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

// ── Editorial story (craft panels + testimonials from /fusion/editorial/) ──
const editorial = ref<FusionEditorial | null>(null);
const editorialError = ref('');
const voiceIndex = ref(0);
let voiceTimer: ReturnType<typeof setInterval> | undefined;

const craftPanels = () => editorial.value?.craft ?? ([] as EditorialCraft[]);
const voices = () => editorial.value?.voices ?? ([] as EditorialVoice[]);

function startVoiceTimer() {
  stopVoiceTimer();
  if (window.matchMedia?.('(prefers-reduced-motion: reduce)').matches) {
    return;
  }
  voiceTimer = setInterval(() => {
    const list = voices();
    if (list.length > 1) {
      voiceIndex.value = (voiceIndex.value + 1) % list.length;
    }
  }, 7000);
}
function stopVoiceTimer() {
  if (voiceTimer) {
    clearInterval(voiceTimer);
    voiceTimer = undefined;
  }
}

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
  // Editorial story — same seeded payload the storefront uses.
  try {
    editorial.value = await getFusionEditorial();
    startVoiceTimer();
  } catch {
    editorialError.value = 'Story unavailable — start the Django portal on :8075.';
  }
});

onUnmounted(stopVoiceTimer);

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
        </CardHeader>
        <div class="mt-5 space-y-4">
          <div>
            <label class="block pb-1.5">
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
          <div class="bezel inline-flex max-w-xs">
            <div class="bezel-core flex items-center">
              <select
                :value="language"
                @change="onLanguageChange"
                class="w-full bg-transparent px-4 py-2.5 pr-8 text-sm font-semibold outline-none"
                aria-label="Language"
              >
                <option v-for="loc in SUPPORTED_LOCALES" :key="loc" :value="loc">
                  {{ t(`settings.languages.${loc}`) }}
                </option>
              </select>
            </div>
          </div>
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

    <!-- The story — craft panels + testimonials from /fusion/editorial/ -->
    <div class="bezel pos-reveal" :class="revealed ? 'is-visible' : ''" style="transition-delay: 320ms">
      <div class="bezel-core p-6 sm:p-7">
        <CardHeader class="p-0">
          <CardTitle>About the café</CardTitle>
          <CardDescription>Roast, kitchen, pickup — the story from the Django portal.</CardDescription>
        </CardHeader>

        <p v-if="editorialError" class="mt-4 rounded-xl border border-error/20 bg-error/5 px-4 py-3 text-sm text-error">
          {{ editorialError }}
        </p>

        <template v-else-if="craftPanels().length">
          <!-- Craft panels — three chapter cards with seeded imagery -->
          <div class="mt-6 grid gap-4 md:grid-cols-3">
            <article
              v-for="panel in craftPanels()"
              :key="panel.title"
              class="group relative flex min-h-[13rem] flex-col justify-end overflow-hidden rounded-[1.25rem] border border-base-300/60 bg-base-200/60"
            >
              <img
                :src="panel.img"
                :alt="panel.alt"
                loading="lazy"
                class="absolute inset-0 h-full w-full object-cover opacity-85 contrast-110 saturate-[0.8] transition-transform duration-700 ease-[cubic-bezier(0.32,0.72,0,1)] group-hover:scale-[1.04]"
              />
              <div class="absolute inset-0 bg-gradient-to-t from-base-100/90 via-base-100/25 to-transparent" aria-hidden="true"></div>
              <div class="relative p-4">
                <p class="font-mono text-[0.6rem] font-semibold uppercase tracking-[0.18em] text-base-content/60">
                  {{ panel.caption }}
                </p>
                <h3 class="mt-1 font-display text-lg font-bold tracking-tight">{{ panel.title }}</h3>
                <p class="mt-1.5 text-xs leading-relaxed text-base-content/65">{{ panel.body }}</p>
              </div>
            </article>
          </div>

          <!-- Testimonial — rotating quote, paused on hover, static under reduced motion -->
          <div
            v-if="voices().length"
            class="bezel mt-5"
            @mouseenter="stopVoiceTimer()"
            @mouseleave="startVoiceTimer()"
          >
            <div class="bezel-core flex flex-col gap-4 p-5 sm:flex-row sm:items-center sm:gap-5">
              <template v-for="(voice, vi) in voices()" :key="voice.name">
                <div
                  v-show="voiceIndex === vi"
                  class="flex items-center gap-4"
                >
                  <img
                    :src="voice.img"
                    :alt="voice.name"
                    loading="lazy"
                    class="h-14 w-14 shrink-0 rounded-full border-2 border-base-300 object-cover grayscale contrast-125"
                  />
                  <div>
                    <p class="font-display text-base font-bold leading-snug tracking-tight">
                      “{{ voice.quote }}”
                    </p>
                    <p class="mt-1.5 text-sm font-semibold">{{ voice.name }}</p>
                    <p class="font-mono text-[0.6rem] uppercase tracking-widest text-base-content/45">{{ voice.role }}</p>
                  </div>
                </div>
              </template>
              <div v-if="voices().length > 1" class="flex shrink-0 items-center gap-1.5 sm:ml-auto">
                <button
                  v-for="(voice, vi) in voices()"
                  :key="`dot-${voice.name}`"
                  type="button"
                  class="h-1.5 rounded-full transition-all duration-500 ease-[cubic-bezier(0.32,0.72,0,1)]"
                  :class="voiceIndex === vi ? 'w-6 bg-primary' : 'w-1.5 bg-base-content/20 hover:bg-base-content/40'"
                  :aria-label="`Show quote from ${voice.name}`"
                  @click="voiceIndex = vi"
                ></button>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>
