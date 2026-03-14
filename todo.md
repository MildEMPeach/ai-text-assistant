# TODO - AI Text Assistant

## Phase 1: 项目初始化与工程化

- [x] 初始化 Electron + TypeScript 项目结构
- [x] 配置 main / preload / renderer 构建链路
- [x] 接入 ESLint、Prettier、基础 tsconfig
- [x] 实现托盘、主窗口与气泡窗口
- [x] 实现本地配置存储

## Phase 2: 文本触发链路

- [x] 实现剪贴板轮询监听与长度过滤
- [x] 实现全局快捷键 `Ctrl/Cmd + Shift + L`
- [x] 实现文本捕获后显示浮动气泡
- [x] 实现点击气泡后打开主面板并注入文本

## Phase 3: 多模型 Provider 适配

- [x] 设计统一的 `LLMProvider` 接口
- [x] 实现 OpenAI Compatible Provider
- [x] 实现 DeepSeek Provider
- [x] 实现 Anthropic Provider
- [x] 实现 Gemini Provider
- [x] 实现 `TaskOrchestrator`，支持总结、翻译、自定义处理

## Phase 4: UI 与基础质量

- [x] 完成主面板 UI
- [x] 完成设置面板 UI
- [x] 完成加载态、错误提示、结果复制交互
- [x] 完成日志与错误收集
- [x] 完成基础运行校验：`typecheck` / `build`

## 当前状态

- [x] 应用可托盘常驻
- [x] 支持复制文本后弹出气泡
- [x] 支持通过气泡或快捷键打开主面板
- [x] 支持 4 类 Provider 接入
- [x] 当前代码结构已具备继续扩展的基础

## 后续可选项

- [ ] 接入系统级选区监听，替代 MVP 的剪贴板近似方案
- [ ] 增加打包与发布流程
- [ ] 增加自动化测试
- [ ] 补充启动即运行、开机自启等桌面能力
