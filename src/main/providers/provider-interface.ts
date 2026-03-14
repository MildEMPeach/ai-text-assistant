import type { ProviderConfig } from '../../shared/types';

export interface LLMProvider {
  summarize(input: string): Promise<string>;
  translate(input: string, targetLanguage: string): Promise<string>;
  custom(input: string, prompt: string): Promise<string>;
}

export abstract class BaseProvider implements LLMProvider {
  protected readonly config: ProviderConfig;

  constructor(config: ProviderConfig) {
    this.config = config;
  }

  abstract summarize(input: string): Promise<string>;
  abstract translate(input: string, targetLanguage: string): Promise<string>;
  abstract custom(input: string, prompt: string): Promise<string>;

  protected assertConfigured(): void {
    if (!this.config.apiKey) {
      throw new Error('API Key is not configured.');
    }
    if (!this.config.model) {
      throw new Error('Model is not configured.');
    }
  }
}
