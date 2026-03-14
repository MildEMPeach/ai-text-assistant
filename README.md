# AI Text Assistant

桌面端 AI 文本助手。应用常驻托盘，监听剪贴板文本变化，在鼠标附近弹出轻量气泡，点击后可对文本执行总结、翻译或自定义处理。

## 已实现能力

- Electron + TypeScript 分层结构：`main` / `preload` / `renderer`
- 系统托盘常驻、单实例运行、全局快捷键 `Ctrl/Cmd + Shift + L`
- 基于剪贴板轮询的文本捕获与去重过滤
- 鼠标附近悬浮气泡，点击后打开主面板
- 主面板支持原文输入、总结、翻译、自定义提示词处理
- 设置面板支持 Provider、Model、API Key、Base URL、目标语言
- 多模型适配：
  - OpenAI Compatible
  - DeepSeek
  - Anthropic
  - Gemini

## 项目结构

- `docs/architecture.md`：架构设计说明
- `todo.md`：迭代状态与待办
- `src/main`：主进程，负责窗口、托盘、监听、Provider、IPC
- `src/preload`：安全桥接 API
- `src/renderer`：气泡与主面板 UI
- `src/shared`：共享类型与 IPC 协议

## 本地开发

```bash
npm install
npm run dev
```

如果在 PowerShell 中遇到 `npm.ps1` 执行策略限制，可改用：

```bash
npm.cmd install
npm.cmd run dev
```

## 构建与启动

```bash
npm run build
npm start
```

## 使用方式

1. 启动应用后，程序常驻系统托盘。
2. 打开主面板，先配置 `Provider`、`Model`、`API Key`、`Base URL`、`目标语言`。
3. 在任意应用中复制一段文本，鼠标附近会出现 `AI` 气泡。
4. 点击气泡打开主面板，或在复制文本后按 `Ctrl/Cmd + Shift + L` 直接打开主面板。
5. 在主面板中选择“总结”“翻译”或“自定义处理”，查看并复制结果。

## 默认 Provider 预设

- OpenAI Compatible
  - Model: `gpt-4o-mini`
  - Base URL: `https://api.openai.com/v1`
- DeepSeek
  - Model: `deepseek-chat`
  - Base URL: `https://api.deepseek.com/v1`
- Anthropic
  - Model: `claude-3-5-sonnet-latest`
- Gemini
  - Model: `gemini-1.5-flash`
  - Base URL: `https://generativelanguage.googleapis.com/v1beta`

## 当前限制

- 当前版本的“选中文本触发”属于 MVP，实现方式是监听剪贴板变化，不是系统级原生选区监听。
- 更稳妥的交互方式仍然是“先复制，再点击气泡”或“先复制，再按快捷键”。

## 验证状态

以下命令已在本地通过：

- `npm.cmd run typecheck`
- `npm.cmd run build`
