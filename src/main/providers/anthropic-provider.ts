import Anthropic from '@anthropic-ai/sdk';

import type { ProviderConfig } from '../../shared/types';
import { BaseProvider } from './provider-interface';

export class AnthropicProvider extends BaseProvider {
  private readonly client: Anthropic;

  constructor(config: ProviderConfig) {
    super(config);
    this.client = new Anthropic({
      apiKey: config.apiKey,
      baseURL: config.baseUrl
    });
  }

  async summarize(input: string): Promise<string> {
    return this.complete(
      'You are a concise assistant. Summarize the provided text in clear bullet points. Keep key facts and decisions.',
      input
    );
  }

  async translate(input: string, targetLanguage: string): Promise<string> {
    return this.complete(
      `You are a professional translator. Translate the user text into ${targetLanguage}. Keep meaning accurate and natural.`,
      input
    );
  }

  async custom(input: string, prompt: string): Promise<string> {
    return this.complete(prompt, input);
  }

  private async complete(systemPrompt: string, userText: string): Promise<string> {
    this.assertConfigured();

    const message = await this.client.messages.create({
      model: this.config.model,
      max_tokens: 1024,
      system: systemPrompt,
      messages: [{ role: 'user', content: userText }]
    });

    const output = message.content
      .map((block) => {
        if ('text' in block && typeof block.text === 'string') {
          return block.text;
        }
        return '';
      })
      .join('\n')
      .trim();

    if (!output) {
      throw new Error('No text content returned by Anthropic API.');
    }

    return output;
  }
}
