<template>
    <header class="sticky top-0 z-40 px-4 pt-4">
        <!-- ── Fluid Island pill ─────────────────────────────────────────── -->
        <div
            class="relative mx-auto flex h-14 max-w-[1280px] items-center justify-between gap-3 rounded-full border border-base-300/70 bg-base-100/85 px-3 pl-2 shadow-[0_8px_32px_-12px_hsl(var(--pos-ink)/0.12),inset_0_1px_0_hsl(0_0%_100%/0.6)] backdrop-blur-xl"
        >
            <!-- Hamburger → X morph -->
            <button
                type="button"
                class="group relative flex h-10 w-10 items-center justify-center rounded-full transition-all duration-500 ease-[cubic-bezier(0.32,0.72,0,1)] hover:bg-base-200/80 active:scale-95"
                :aria-label="open ? 'Close menu' : 'Open menu'"
                :aria-expanded="open"
                @click="toggle"
            >
                <span
                    class="absolute h-[1.5px] w-4 rounded-full bg-base-content transition-all duration-500 ease-[cubic-bezier(0.32,0.72,0,1)]"
                    :class="open ? 'rotate-45' : '-translate-y-[4.5px]'"
                />
                <span
                    class="absolute h-[1.5px] w-4 rounded-full bg-base-content transition-all duration-500 ease-[cubic-bezier(0.32,0.72,0,1)]"
                    :class="open ? '-rotate-45' : 'translate-y-[4.5px]'"
                />
            </button>

            <!-- Brand mark + wordmark -->
            <div class="flex flex-1 items-center gap-2.5 pl-2">
                <svg class="h-7 w-7" viewBox="0 0 32 32" fill="none" aria-hidden="true">
                    <rect width="32" height="32" rx="9" fill="hsl(var(--pos-ink))" />
                    <path
                        d="M8 12l6 6-6 6"
                        stroke="#FFE14D"
                        stroke-width="2.2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                    />
                    <circle cx="21" cy="14" r="3.2" fill="hsl(var(--pos-verdigris))" />
                    <path d="M21 17.2v6" stroke="hsl(var(--pos-verdigris))" stroke-width="2.2" stroke-linecap="round" />
                </svg>
                <span class="hidden text-sm font-semibold tracking-tight sm:inline">Formint Client</span>
            </div>

            <div class="flex flex-none items-center gap-2">
                <!-- Client version chip -->
                <span
                    class="mr-1 hidden rounded-full border border-base-300/80 px-2.5 py-1 font-mono text-[0.65rem] font-semibold tracking-wider text-base-content/50 lg:inline"
                    title="Client version"
                >
                    v{{ version }}
                </span>
                <!-- Theme toggle — liquid swap -->
                <button
                    type="button"
                    class="relative flex h-10 w-10 items-center justify-center rounded-full border border-base-300/70 bg-base-100/60 text-base-content/70 transition-all duration-500 ease-[cubic-bezier(0.32,0.72,0,1)] hover:text-base-content active:scale-95"
                    :aria-label="t('settings.toggleTheme')"
                    @click="handleThemeToggle"
                >
                    <Icon
                        name="sun"
                        class="absolute h-[18px] w-[18px] transition-all duration-500 ease-[cubic-bezier(0.32,0.72,0,1)]"
                        :class="
                            isDark
                                ? 'rotate-90 scale-0 opacity-0'
                                : 'rotate-0 scale-100 opacity-100'
                        "
                    />
                    <Icon
                        name="moon"
                        class="absolute h-[18px] w-[18px] transition-all duration-500 ease-[cubic-bezier(0.32,0.72,0,1)]"
                        :class="
                            isDark
                                ? 'rotate-0 scale-100 opacity-100'
                                : '-rotate-90 scale-0 opacity-0'
                        "
                    />
                </button>
            </div>
        </div>
    </header>

    <!-- ── Full-screen glass overlay menu ───────────────────────────────── -->
    <Transition
        enter-active-class="transition duration-500 ease-[cubic-bezier(0.32,0.72,0,1)]"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition duration-300 ease-[cubic-bezier(0.32,0.72,0,1)]"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
    >
        <div
            v-if="open"
            class="fixed inset-0 z-30 overflow-y-auto bg-base-100/90 backdrop-blur-3xl"
            @click.self="close"
        >
            <div class="mx-auto flex min-h-[100dvh] w-full max-w-[1280px] flex-col justify-center px-8 pb-16 pt-28 sm:px-12">
                <!-- Staggered mask reveal — links rise out of a hidden box -->
                <p class="eyebrow w-max">Navigation</p>
                <nav class="mt-10" aria-label="Main">
                    <ul class="space-y-2">
                        <li
                            v-for="(item, i) in nav"
                            :key="item.to"
                            class="nav-mask overflow-hidden"
                            :style="{ transitionDelay: `${120 + i * 70}ms` }"
                        >
                            <router-link
                                :to="item.to"
                                class="group flex items-center gap-5 py-3 sm:py-4"
                                @click="close"
                            >
                                <span
                                    class="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl border transition-all duration-500 ease-[cubic-bezier(0.32,0.72,0,1)]"
                                    :class="
                                        route.path === item.to
                                            ? 'border-base-content/10 bg-base-content text-base-100'
                                            : 'border-base-300/70 bg-base-100/60 text-base-content/50 group-hover:scale-105 group-hover:text-base-content'
                                    "
                                >
                                    <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" :d="item.icon" />
                                    </svg>
                                </span>
                                <span
                                    class="font-display text-3xl font-bold tracking-tight transition-colors duration-500 ease-[cubic-bezier(0.32,0.72,0,1)] sm:text-5xl"
                                    :class="
                                        route.path === item.to
                                            ? 'text-base-content'
                                            : 'text-base-content/40 group-hover:text-base-content'
                                    "
                                >
                                    {{ item.label }}
                                </span>
                                <span
                                    class="ml-auto font-mono text-xs tracking-[0.2em] text-base-content/30 transition-all duration-500 ease-[cubic-bezier(0.32,0.72,0,1)] group-hover:-translate-y-0.5 group-hover:text-base-content/60"
                                >
                                    0{{ i + 1 }}
                                </span>
                            </router-link>
                        </li>
                    </ul>
                </nav>

                <!-- Overlay footer: version + hint -->
                <div class="mt-16 flex flex-wrap items-center gap-3 border-t border-base-300/60 pt-6">
                    <span class="font-mono text-[0.65rem] font-semibold uppercase tracking-[0.2em] text-base-content/40">
                        Formint Client · v{{ version }}
                    </span>
                    <span class="ml-auto hidden font-mono text-[0.65rem] uppercase tracking-[0.2em] text-base-content/30 sm:inline">
                        Esc to close
                    </span>
                </div>
            </div>
        </div>
    </Transition>
</template>

<script setup lang="ts">
    import { ref, computed, onMounted, onUnmounted, watch, nextTick } from "vue";
    import { useRoute } from "vue-router";
    import Icon from "@/components/ui/Icon.vue";
    import { useSettingsStore } from "../utils/settings";
    import { useTheme } from "../utils/theme";
    import { useLanguage } from "../utils/i18n";
    import { getClientVersion } from "../utils/version";

    const settingsStore = useSettingsStore();
    const { toggleTheme } = useTheme();
    const { t } = useLanguage();
    const route = useRoute();

    const version = ref("…");
    onMounted(() => {
        getClientVersion().then((v) => (version.value = v));
    });

    const isDark = computed(() => settingsStore.theme === "sunset");

    const handleThemeToggle = async () => {
        await toggleTheme();
    };

    // ── Overlay menu state ────────────────────────────────────────────────
    const open = ref(false);
    const toggle = () => (open.value = !open.value);
    const close = () => (open.value = false);

    // Close when the route changes (nav click) or Esc is pressed.
    watch(
        () => route.path,
        () => close(),
    );

    const onKey = (e: KeyboardEvent) => {
        if (e.key === "Escape") {
            close();
        }
    };
    onMounted(() => window.addEventListener("keydown", onKey));
    onUnmounted(() => window.removeEventListener("keydown", onKey));

    // Lock body scroll while the overlay is open (fixed overlay needs a
    // stable background; toggling overflow is layout-safe, not animated).
    watch(open, async (isOpen) => {
        document.body.style.overflow = isOpen ? "hidden" : "";
        // Staggered mask reveal: links rise out of their hidden box once
        // the glass fade-in starts. Reduced-motion users get instant text.
        await nextTick();
        document.querySelectorAll<HTMLElement>(".nav-mask").forEach((el) => {
            el.classList.toggle("is-visible", isOpen);
        });
    });
    onUnmounted(() => {
        document.body.style.overflow = "";
    });

    const nav = computed(() => [
        { to: "/", label: t("navigation.home"), icon: "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" },
        { to: "/menu", label: t("navigation.menu"), icon: "M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" },
        { to: "/orders", label: t("navigation.orders"), icon: "M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" },
        { to: "/settings", label: t("navigation.settings"), icon: "M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" },
    ]);
</script>
