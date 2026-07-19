# Tauri Vue3 应用模板

**中文** | [English](README.md)

一个现代化的跨平台桌面应用程序模板，基于 Tauri v2 和 Vue 3 构建，具有国际化、主题切换和多页面清洁响应式 UI。

## 特性

- **现代技术栈**: Tauri v2 + Vue 3 + TypeScript + Vite
- **样式设计**: Tailwind CSS v4 + daisyUI 组件
- **国际化**: 内置 i18n 支持（英文和中文）
- **状态管理**: Pinia 状态管理器，支持不依赖localStorage的本地持久化设置
- **主题系统**: 动态主题切换，支持 daisyUI 主题
- **响应式设计**: 移动优先的响应式布局
- **开发体验**: 热重载、TypeScript、OxLint、Prettier
- **自定义窗口**: 自定义标题栏和窗口控件
- **跨平台**: 支持 Windows、macOS 和 Linux

## 快速开始

### 前置要求

- [Node.js](https://nodejs.org/) (v18 或更高版本)
- [pnpm](https://pnpm.io/) 包管理器
- [Rust](https://rustup.rs/) 工具链

### 安装

1. **克隆仓库**

    ```bash
    git clone https://github.com/KitsuneX07/tauri-vue-app.git
    cd tauri-vue-app
    ```

2. **安装依赖**

    ```bash
    pnpm install
    ```

3. **启动开发服务器**

    ```bash
    pnpm tauri dev
    ```

4. **构建生产版本**
    ```bash
    pnpm tauri build
    ```

## 开发命令

### 前端开发

```bash
pnpm dev          # 启动 Vue 开发服务器 (端口 1420)
pnpm build        # 构建 Vue 前端生产版本
pnpm preview      # 预览生产版本
```

### Tauri 开发

```bash
pnpm tauri dev    # 启动 Tauri 开发环境
pnpm tauri build  # 构建 Tauri 应用程序
pnpm tauri        # 访问 Tauri CLI 命令
```

### 代码质量

```bash
pnpm lint         # 运行 oxlint 进行代码检查
pnpm lint:fix     # 运行 oxlint 并自动修复
pnpm format       # 使用 Prettier 格式化代码
vue-tsc --noEmit  # TypeScript 类型检查
```

## 项目结构

```
tauri-vue-app/
├── src/                    # Vue 前端源代码
│   ├── components/         # 可重用的 Vue 组件
│   │   └── TitleBar.vue   # 自定义标题栏组件
│   ├── layouts/           # 布局组件
│   │   └── MainLayout.vue # 主应用程序布局
│   ├── views/             # 页面组件
│   │   ├── HomeView.vue   # 首页
│   │   └── SettingsView.vue # 设置页面
│   ├── utils/             # 工具函数
│   │   ├── i18n.ts        # 国际化设置
│   │   ├── settings.ts    # 设置管理
│   │   └── theme.ts       # 主题切换工具
│   ├── locales/           # 翻译文件
│   │   ├── en-US.ts       # 英文翻译
│   │   └── zh-CN.ts       # 中文翻译
│   ├── router/            # Vue Router 配置
│   │   └── index.ts       # 路由设置
│   ├── assets/            # 静态资源
│   │   └── main.css       # 全局样式
│   ├── App.vue            # 根组件
│   └── main.ts            # Vue 应用入口点
├── src-tauri/             # Rust 后端源代码
│   ├── src/
│   │   ├── main.rs        # Tauri 应用入口点
│   │   └── lib.rs         # 主 Rust 库
│   ├── icons/             # 应用图标
│   ├── Cargo.toml         # Rust 依赖
│   └── tauri.conf.json    # Tauri 配置
├── public/                # 公共资源
├── package.json           # Node.js 依赖
├── vite.config.ts         # Vite 配置
├── tailwind.config.ts     # Tailwind CSS 配置
├── tsconfig.json          # TypeScript 配置
└── README.md              # 本文件
```

## 技术栈

### 前端

- **Vue 3** - 渐进式 JavaScript 框架，使用 Composition API
- **TypeScript** - 类型安全的 JavaScript 开发
- **Vite** - 快速构建工具和开发服务器
- **Vue Router** - 客户端路由
- **Pinia** - 状态管理
- **Vue i18n** - 国际化
- **Tailwind CSS v4** - 实用优先的 CSS 框架
- **daisyUI** - Tailwind CSS 组件
- **Heroicons** - 精美的手工制作 SVG 图标

### 后端

- **Rust** - 系统编程语言
- **Tauri v2** - 跨平台桌面应用框架
- **Tauri 插件**:
    - `store` - 持久化键值存储
    - `fs` - 文件系统操作
    - `opener` - 打开 URL 和文件
    - `log` - 日志记录功能

### 开发工具

- **oxlint** - 快速的 JavaScript/TypeScript 代码检查器
- **Prettier** - 代码格式化工具，支持 Tailwind 插件
- **pnpm** - 快速、节省磁盘空间的包管理器

## 配置

### 国际化

应用程序开箱即用支持多种语言：

- 英文 (en-US)
- 中文 (zh-CN)

通过在 `src/locales/` 中创建翻译文件并更新 i18n 配置来添加新语言。

### 主题系统

内置主题切换，支持 daisyUI 主题：

- 浅色主题：light、pastel、emerald
- 深色主题：dark、forest、luxury

在 `src/utils/theme.ts` 中自定义主题。

### 设置持久化

用户设置使用 Tauri 的 store 插件自动保存：

- 语言偏好
- 主题选择
- 窗口状态
- 自定义配置

## 构建和分发

### 开发构建

```bash
pnpm tauri dev
```

### 生产构建

```bash
pnpm tauri build
```

构建输出生成在 `src-tauri/target/release/bundle/`:

- **Windows**: `.msi` 安装程序和 `.exe` 可执行文件
- **macOS**: `.dmg` 安装程序和 `.app` 应用包
- **Linux**: `.deb`、`.rpm` 和 `.AppImage` 包

### 自定义设置

1. **应用标识**: 更新 `src-tauri/tauri.conf.json`
2. **图标**: 替换 `src-tauri/icons/` 中的文件
3. **窗口设置**: 修改 `tauri.conf.json` 中的窗口配置
4. **品牌**: 更新应用名称、描述和元数据

## IDE 设置

### 推荐的 IDE 设置

- [VS Code](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) + [Tauri](https://marketplace.visualstudio.com/items?itemName=tauri-apps.tauri-vscode) + [rust-analyzer](https://marketplace.visualstudio.com/items?itemName=rust-lang.rust-analyzer)

### TS 中 `.vue` 导入的类型支持

由于 TypeScript 无法处理 `.vue` 导入的类型信息，默认情况下它们被设置为通用的 Vue 组件类型。在大多数情况下，如果您不太关心模板外部的组件属性类型，这是可以的。但是，如果您希望在 `.vue` 导入中获得实际的属性类型（例如，在使用手动 `h(...)` 调用时获得属性验证），您可以通过以下步骤启用 Volar 的接管模式：

1. 从 VS Code 的命令面板运行 `Extensions: Show Built-in Extensions`，查找 `TypeScript and JavaScript Language Features`，然后右键单击并选择 `Disable (Workspace)`。默认情况下，如果禁用了默认的 TypeScript 扩展，接管模式将自动启用。
2. 通过从命令面板运行 `Developer: Reload Window` 来重新加载 VS Code 窗口。

您可以在[这里](https://github.com/johnsoncodehk/volar/discussions/471)了解更多关于接管模式的信息。

## 贡献

1. Fork 仓库
2. 创建功能分支：`git checkout -b feature/amazing-feature`
3. 提交您的更改：`git commit -m 'Add amazing feature'`
4. 推送到分支：`git push origin feature/amazing-feature`
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 致谢

- [Tauri](https://tauri.app/) - 提供了出色的跨平台框架
- [Vue.js](https://vuejs.org/) - 提供了响应式前端框架
- [Tailwind CSS](https://tailwindcss.com/) - 提供了实用优先的 CSS 框架
- [daisyUI](https://daisyui.com/) - 提供了精美的组件库

## 支持

如果您觉得这个模板有帮助，请考虑：

- 为仓库点星
- 报告问题
- 贡献改进
- 分享反馈
