import type { ProviderType } from './types';

export interface ProviderPreset {
  label: string;
  defaultModel: string;
  defaultBaseUrl?: string;
}

export const PROVIDER_PRESETS: Record<ProviderType, ProviderPreset> = {
  'openai-compatible': {
    label: 'OpenAI Compatible',
    defaultModel: 'gpt-4o-mini',
    defaultBaseUrl: 'https://api.openai.com/v1'
  },
  anthropic: {
    label: 'Anthropic',
    defaultModel: 'claude-3-5-sonnet-latest'
  },
  gemini: {
    label: 'Gemini',
    defaultModel: 'gemini-1.5-flash',
    defaultBaseUrl: 'https://generativelanguage.googleapis.com/v1beta'
  },
  deepseek: {
    label: 'DeepSeek',
    defaultModel: 'deepseek-chat',
    defaultBaseUrl: 'https://api.deepseek.com/v1'
  }
};
