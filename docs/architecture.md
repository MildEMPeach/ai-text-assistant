# AI Text Assistant 架构设计

## 1. 目标

构建一个常驻托盘的桌面 AI 文本助手：

- 用户在任意应用中复制文本后，鼠标附近出现轻量气泡
- 点击气泡后打开主面板，对文本执行总结、翻译或自定义处理
- 通过统一适配层支持多个大模型 Provider
- 结构清晰，便于继续扩展为更完整的桌面工具

## 2. 技术选型

- 桌面框架：Electron + TypeScript
- 渲染层：HTML / CSS / TypeScript
- 主进程构建：`tsc`
- 渲染层构建：`vite`
- 本地配置：`electron-store`
- 日志：`electron-log`
- 参数校验：`zod`

## 3. 分层结构

```text
src/
  main/      主进程：托盘、窗口、监听、IPC、Provider、任务编排
  preload/   通过 contextBridge 暴露安全 API
  renderer/  气泡窗口与主面板 UI
  shared/    共享类型、Provider 预设、IPC 常量
```

## 4. 核心模块

### SelectionMonitor

- 轮询剪贴板文本变化
- 过滤过短、过长和重复文本
- 支持快捷键触发，从当前剪贴板直接打开面板
- 输出统一事件：`{ text, cursor, source, timestamp }`

### BubbleWindow

- 在鼠标附近展示轻量气泡
- 点击后通知主进程打开主面板
- 超时自动隐藏

### PanelWindow

- 承载主交互界面
- 注入待处理文本
- 展示执行状态、模型信息和结果

### TaskOrchestrator

- 根据动作类型生成调用请求
- 调用 Provider 执行总结、翻译或自定义任务
- 返回统一结果结构

### ProviderFactory

- 根据当前配置创建目标 Provider
- 屏蔽不同模型 API 的差异

### ConfigStore

- 管理 Provider、模型、API Key、Base URL、目标语言
- 保存 UI 相关参数，例如轮询间隔和气泡自动隐藏时间

## 5. Provider 策略

统一接口：

```ts
interface LLMProvider {
  summarize(input: string): Promise<string>;
  translate(input: string, targetLanguage: string): Promise<string>;
  custom(input: string, prompt: string): Promise<string>;
}
```

当前支持：

- OpenAI Compatible
- DeepSeek
- Anthropic
- Gemini

## 6. 主流程

### 自动触发流程

1. 用户复制文本
2. `SelectionMonitor` 检测到剪贴板变化
3. 主进程记录文本并显示气泡
4. 用户点击气泡
5. 主面板打开并注入文本
6. 用户选择总结、翻译或自定义处理
7. `TaskOrchestrator` 调用对应 Provider
8. 渲染层展示结果并支持复制

### 快捷键流程

1. 用户复制文本
2. 按下 `Ctrl/Cmd + Shift + L`
3. 主进程直接读取剪贴板文本
4. 主面板打开并注入文本

## 7. 安全与约束

- 渲染层通过 `preload` 和 `contextBridge` 与主进程通信
- 主进程 IPC 入参通过 `zod` 校验
- API Key 保存在本地配置，不写入源码
- 当前版本仍使用剪贴板轮询，不是原生系统选区监听

## 8. 后续演进方向

- 接入系统级文本选区监听
- 增加自动化测试
- 增加桌面打包、安装与发布能力
- 完善启动项、自启与更细粒度的设置项
