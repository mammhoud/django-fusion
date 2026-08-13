import { defineStore } from "pinia";
import { Store } from "@tauri-apps/plugin-store";

export interface UserSettings {
    theme: "cupcake" | "sunset";
    language: "en-US" | "zh-CN";
}

const defaultSettings: UserSettings = {
    theme: "cupcake",
    language: "zh-CN",
};

let diskStore: Store | null = null;

export const useSettingsStore = defineStore("settings", {
    state: (): UserSettings => ({
        ...defaultSettings,
    }),

    actions: {
        async initializeSettings() {
            try {
                if (!diskStore) {
                    diskStore = await Store.load("settings.json");
                }
                const loadedSettings = await diskStore.get<UserSettings>("userSettings");
                if (loadedSettings) {
                    this.$patch(loadedSettings);
                    console.log("设置已加载:", loadedSettings);
                } else {
                    console.log("未找到保存的设置，使用默认设置");
                }
            } catch (error) {
                console.error("Failed to load settings:", error);
            }
        },

        async updateAndSaveSettings(newSettings: Partial<UserSettings>) {
            try {
                if (!diskStore) {
                    diskStore = await Store.load("settings.json");
                }
                this.$patch(newSettings);
                await diskStore.set("userSettings", this.$state);
                await diskStore.save();
                console.log("设置已保存:", this.$state);
            } catch (error) {
                console.error("Failed to save settings:", error);
            }
        },
    },
});
