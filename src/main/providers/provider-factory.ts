import type { ProviderConfig } from '../../shared/types';

import { AnthropicProvider } from './anthropic-provider';
import { DeepSeekProvider } from './deepseek-provider';
import { GeminiProvider } from './gemini-provider';
import { OpenAICompatibleProvider } from './openai-compatible-provider';
import type { LLMProvider } from './provider-interface';

export function createProvider(config: ProviderConfig): LLMProvider {
  switch (config.type) {
    case 'openai-compatible':
      return new OpenAICompatibleProvider(config);
    case 'anthropic':
      return new AnthropicProvider(config);
    case 'gemini':
      return new GeminiProvider(config);
    case 'deepseek':
      return new DeepSeekProvider(config);
    default:
      throw new Error(`Unsupported provider type: ${String(config.type)}`);
  }
}
