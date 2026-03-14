import { BaseProvider } from './provider-interface';

interface ChatCompletionResponse {
  choices?: Array<{
    message?: {
      content?: string | Array<{ text?: string }>;
    };
  }>;
  error?: {
    message?: string;
  };
}

export class OpenAICompatibleProvider extends BaseProvider {
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

    const baseUrl = this.config.baseUrl || 'https://api.openai.com/v1';
    const endpoint = `${baseUrl.replace(/\/$/, '')}/chat/completions`;
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${this.config.apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: this.config.model,
        temperature: 0.2,
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userText }
        ]
      })
    });

    const payload = (await response.json()) as ChatCompletionResponse;
    if (!response.ok) {
      throw new Error(payload.error?.message || `OpenAI-compatible API failed: ${response.status}`);
    }

    const content = payload.choices?.[0]?.message?.content;
    if (typeof content === 'string') {
      return content.trim();
    }

    if (Array.isArray(content)) {
      const merged = content.map((item) => item.text || '').join('\n').trim();
      if (merged) {
        return merged;
      }
    }

    throw new Error('No text content returned by OpenAI-compatible API.');
  }
}
