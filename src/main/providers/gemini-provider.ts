import { BaseProvider } from './provider-interface';

interface GeminiResponse {
  candidates?: Array<{
    content?: {
      parts?: Array<{
        text?: string;
      }>;
    };
  }>;
  error?: {
    message?: string;
  };
}

export class GeminiProvider extends BaseProvider {
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

    const baseUrl = this.config.baseUrl || 'https://generativelanguage.googleapis.com/v1beta';
    const endpoint = `${baseUrl.replace(/\/$/, '')}/models/${encodeURIComponent(this.config.model)}:generateContent?key=${encodeURIComponent(this.config.apiKey)}`;

    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        systemInstruction: {
          parts: [{ text: systemPrompt }]
        },
        contents: [
          {
            parts: [{ text: userText }]
          }
        ],
        generationConfig: {
          temperature: 0.2
        }
      })
    });

    const payload = (await response.json()) as GeminiResponse;
    if (!response.ok) {
      throw new Error(payload.error?.message || `Gemini API failed: ${response.status}`);
    }

    const output = payload.candidates?.[0]?.content?.parts?.map((part) => part.text || '').join('\n').trim();
    if (!output) {
      throw new Error('No text content returned by Gemini API.');
    }

    return output;
  }
}
