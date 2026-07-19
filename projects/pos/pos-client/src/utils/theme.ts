import { ref, watch } from "vue";
import { useSettingsStore } from "./settings";

const currentTheme = ref<string>("cupcake");

export function useTheme() {
    const settingsStore = useSettingsStore();

    // 应用主题到文档
    const applyTheme = (theme: "cupcake" | "sunset") => {
        // 更新 data-theme 属性
        if (typeof document !== "undefined") {
            document.documentElement.setAttribute("data-theme", theme);
        }

        currentTheme.value = theme;
        return theme;
    };

    // 初始化主题
    const initializeTheme = () => {
        const theme = settingsStore.theme;
        applyTheme(theme);
    };

    // 切换主题（在两个主题之间切换）
    const toggleTheme = async () => {
        const newTheme = settingsStore.theme === "cupcake" ? "sunset" : "cupcake";
        await settingsStore.updateAndSaveSettings({ theme: newTheme });
        applyTheme(newTheme);
    };

    // 设置特定主题
    const setTheme = async (theme: "cupcake" | "sunset") => {
        await settingsStore.updateAndSaveSettings({ theme });
        applyTheme(theme);
    };

    // 监听设置变化
    watch(
        () => settingsStore.theme,
        (newTheme) => {
            applyTheme(newTheme);
        },
    );

    return {
        currentTheme: currentTheme.value,
        initializeTheme,
        toggleTheme,
        setTheme,
        applyTheme,
    };
}
