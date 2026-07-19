import "./assets/main.css";
import { createApp } from "vue";
import { createPinia } from "pinia";
import { createI18n } from "vue-i18n";
import App from "./App.vue";
import router from "./router";
import { useSettingsStore } from "./utils/settings";
import { useTheme } from "./utils/theme";

import zhCN from "./locales/zh-CN.ts";
import enUS from "./locales/en-US.ts";

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
    i18n.global.locale.value = settingsStore.language as "zh-CN" | "en-US";

    app.mount("#app");
})();
