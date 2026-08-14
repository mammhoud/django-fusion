<template>
    <header class="sticky top-0 z-40 px-4 pt-4">
        <div
            class="mx-auto flex h-14 max-w-[1280px] items-center justify-between gap-3 rounded-full border border-base-300/70 bg-base-100/85 px-3 pl-4 shadow-[0_8px_32px_-12px_hsl(var(--pos-ink)/0.12),inset_0_1px_0_hsl(0_0%_100%/0.6)] backdrop-blur-xl"
        >
            <div class="flex-none">
                <div class="dropdown">
                    <div
                        tabindex="0"
                        role="button"
                        class="btn btn-circle btn-ghost btn-sm"
                        aria-label="Menu"
                    >
                        <Bars3Icon class="h-5 w-5" />
                    </div>
                    <ul
                        tabindex="0"
                        class="menu menu-sm dropdown-content mt-3 w-56 rounded-2xl border border-base-300 bg-base-100 p-2 shadow-xl"
                    >
                        <li>
                            <router-link to="/" @click="closeDropdown">
                                {{ t("navigation.home") }}
                            </router-link>
                        </li>
                        <li>
                            <router-link to="/menu" @click="closeDropdown">
                                {{ t("navigation.menu") }}
                            </router-link>
                        </li>
                        <li>
                            <router-link to="/orders" @click="closeDropdown">
                                {{ t("navigation.orders") }}
                            </router-link>
                        </li>
                        <li>
                            <router-link to="/settings" @click="closeDropdown">
                                {{ t("navigation.settings") }}
                            </router-link>
                        </li>
                    </ul>
                </div>
            </div>

            <!-- Brand mark + wordmark -->
            <div class="flex flex-1 items-center gap-2.5">
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

            <div class="flex-none">
                <!-- Client version chip — resolved from the Tauri binary or package.json -->
                <span
                    class="mr-2 hidden rounded-full border border-base-300/80 px-2.5 py-1 font-mono text-[0.65rem] font-semibold tracking-wider text-base-content/50 lg:inline"
                    title="Client version"
                >
                    v{{ version }}
                </span>
                <label class="swap swap-rotate">
                    <input
                        type="checkbox"
                        class="theme-controller"
                        :checked="settingsStore.theme === 'sunset'"
                        @change="handleThemeToggle"
                    />
                    <SunIcon class="swap-off h-5 w-5 fill-current" />
                    <MoonIcon class="swap-on h-5 w-5 fill-current" />
                </label>
            </div>
        </div>
    </header>
</template>

<script setup lang="ts">
    import { ref, onMounted } from "vue";
    import { Bars3Icon, SunIcon, MoonIcon } from "@heroicons/vue/24/outline";
    import { useSettingsStore } from "../utils/settings";
    import { useTheme } from "../utils/theme";
    import { useLanguage } from "../utils/i18n";
    import { getClientVersion } from "../utils/version";

    const settingsStore = useSettingsStore();
    const { toggleTheme } = useTheme();
    const { t } = useLanguage();

    const version = ref("…");
    onMounted(() => {
        getClientVersion().then((v) => (version.value = v));
    });

    const closeDropdown = () => {
        const dropdown = document.activeElement as HTMLElement;
        if (dropdown) {
            dropdown.blur();
        }
    };

    const handleThemeToggle = async () => {
        await toggleTheme();
    };
</script>
