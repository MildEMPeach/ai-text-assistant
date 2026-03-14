import type { ProviderConfig } from '../../shared/types';
import { PROVIDER_PRESETS } from '../../shared/provider-presets';

import { OpenAICompatibleProvider } from './openai-compatible-provider';

export class DeepSeekProvider extends OpenAICompatibleProvider {
  constructor(config: ProviderConfig) {
    super({
      ...config,
      model: config.model || PROVIDER_PRESETS.deepseek.defaultModel,
      baseUrl: config.baseUrl || PROVIDER_PRESETS.deepseek.defaultBaseUrl
    });
  }
}
