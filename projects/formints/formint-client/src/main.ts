import "./assets/main.css";
import "./assets/css/components/_receipt.css";
import "@fontsource-variable/bricolage-grotesque";
import "@fontsource-variable/public-sans";
import "@fontsource-variable/jetbrains-mono";
import { createApp } from "vue";
import { createPinia } from "pinia";
import { createI18n } from "vue-i18n";
import App from "./App.vue";
import router from "./router";
import { useSettingsStore } from "./utils/settings";
import { useTheme } from "./utils/theme";

import zhCN from "./locales/zh-CN.ts";
import enUS from "./locales/en-US.ts";
import arSA from "./locales/ar-SA.ts";
import frFR from "./locales/fr-FR.ts";

const app = createApp(App);
const pinia = createPinia();

// Setup i18n
const i18n = createI18n({
    legacy: false,
    locale: "zh-CN",
    fallbackLocale: "zh-CN",
    messages: {
        "zh-CN": zhCN,
        "en-US": enUS,
        "ar-SA": arSA,
        "fr-FR": frFR,
    },
});

app.use(pinia);
app.use(router);
app.use(i18n);

// Initialize settings, theme, and language
(async () => {
    const settingsStore = useSettingsStore();
    await settingsStore.initializeSettings();

    const { initializeTheme } = useTheme();
    initializeTheme();

    // Initialize language from settings
    i18n.global.locale.value = settingsStore.language;

    app.mount("#app");
})();
