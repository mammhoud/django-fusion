<template>
    <div class="navbar bg-base-100 shadow-sm">
        <div class="flex-none">
            <div class="dropdown">
                <div tabindex="0" role="button" class="btn btn-square btn-ghost">
                    <Bars3Icon class="h-5 w-5" />
                </div>
                <ul
                    tabindex="0"
                    class="menu menu-sm dropdown-content bg-base-100 rounded-box z-[1] mt-3 w-56"
                >
                    <li>
                        <router-link to="/" @click="closeDropdown">{{
                            t("navigation.home")
                        }}</router-link>
                    </li>
                    <li>
                        <router-link to="/settings" @click="closeDropdown">{{
                            t("navigation.settings")
                        }}</router-link>
                    </li>
                </ul>
            </div>
        </div>
        <div class="flex-1">
            <span class="btn btn-ghost normal-case text-xl">Tauri + Vue + daisyUI</span>
        </div>
        <div class="flex-none">
            <label class="swap swap-rotate">
                <!-- this hidden checkbox controls the state -->
                <input
                    type="checkbox"
                    class="theme-controller"
                    :checked="settingsStore.theme === 'sunset'"
                    @change="handleThemeToggle"
                />
                <!-- sun icon -->
                <SunIcon class="swap-off h-10 w-10 fill-current" />
                <!-- moon icon -->
                <MoonIcon class="swap-on h-10 w-10 fill-current" />
            </label>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { Bars3Icon, SunIcon, MoonIcon } from "@heroicons/vue/24/outline";
    import { useSettingsStore } from "../utils/settings";
    import { useTheme } from "../utils/theme";
    import { useLanguage } from "../utils/i18n";

    const settingsStore = useSettingsStore();
    const { toggleTheme } = useTheme();
    const { t } = useLanguage();

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
