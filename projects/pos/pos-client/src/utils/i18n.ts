import { watch } from "vue";
import { useI18n } from "vue-i18n";
import { useSettingsStore } from "./settings";

export function useLanguage() {
    const settingsStore = useSettingsStore();
    const { locale, t } = useI18n();

    // Watch for settings changes and update locale
    watch(
        () => settingsStore.language,
        (newLanguage) => {
            locale.value = newLanguage as "zh-CN" | "en-US";
        },
    );

    // Switch language and save to settings
    const switchLanguage = async (newLanguage: "zh-CN" | "en-US") => {
        await settingsStore.updateAndSaveSettings({ language: newLanguage });
    };

    // Toggle between supported languages
    const toggleLanguage = async () => {
        const newLanguage = settingsStore.language === "zh-CN" ? "en-US" : "zh-CN";
        await switchLanguage(newLanguage);
    };

    return {
        switchLanguage,
        toggleLanguage,
        currentLanguage: () => settingsStore.language,
        t,
    };
}
