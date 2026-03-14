export type ProviderType = 'openai-compatible' | 'anthropic' | 'gemini' | 'deepseek';

export type TaskAction = 'summarize' | 'translate' | 'custom';

export type SelectionSource = 'clipboard' | 'shortcut';

export interface ProviderConfig {
  type: ProviderType;
  apiKey: string;
  model: string;
  baseUrl?: string;
}

export interface UIConfig {
  bubbleAutoHideMs: number;
  clipboardPollMs: number;
  minCaptureLength: number;
  maxCaptureLength: number;
}

export interface AppConfig {
  provider: ProviderConfig;
  targetLanguage: string;
  ui: UIConfig;
}

export interface ConfigUpdatePayload {
  provider?: Partial<ProviderConfig>;
  targetLanguage?: string;
  ui?: Partial<UIConfig>;
}

export interface SelectionPayload {
  text: string;
  source: SelectionSource;
  cursor: {
    x: number;
    y: number;
  };
  timestamp: number;
}

export interface TaskRequest {
  action: TaskAction;
  text: string;
  customPrompt?: string;
  targetLanguage?: string;
}

export interface TaskResult {
  action: TaskAction;
  output: string;
  model: string;
  provider: ProviderType;
  latencyMs: number;
}
