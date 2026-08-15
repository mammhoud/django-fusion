import { watch } from "vue";
import { useI18n } from "vue-i18n";
import { useSettingsStore, type AppLocale } from "./settings";

export const SUPPORTED_LOCALES: AppLocale[] = ["en-US", "zh-CN", "ar-SA", "fr-FR"];
export const RTL_LOCALES: AppLocale[] = ["ar-SA"];

export function useLanguage() {
    const settingsStore = useSettingsStore();
    const { locale, t } = useI18n();

    const applyLocale = (lang: AppLocale) => {
        locale.value = lang;
        document.documentElement.dir = RTL_LOCALES.includes(lang) ? "rtl" : "ltr";
        document.documentElement.lang = lang;
    };

    // Watch for settings changes and update locale (and document direction).
    watch(
        () => settingsStore.language,
        (newLanguage) => applyLocale(newLanguage),
    );

    // Switch language, apply direction, and persist to settings.
    const switchLanguage = async (newLanguage: AppLocale) => {
        applyLocale(newLanguage);
        await settingsStore.updateAndSaveSettings({ language: newLanguage });
    };

    // Cycle through the supported locales.
    const toggleLanguage = async () => {
        const current = settingsStore.language;
        const next = SUPPORTED_LOCALES[(SUPPORTED_LOCALES.indexOf(current) + 1) % SUPPORTED_LOCALES.length];
        await switchLanguage(next);
    };

    return {
        switchLanguage,
        toggleLanguage,
        currentLanguage: () => settingsStore.language,
        t,
    };
}
