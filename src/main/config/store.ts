import Store from 'electron-store';

import { PROVIDER_PRESETS } from '../../shared/provider-presets';
import type { AppConfig, ConfigUpdatePayload } from '../../shared/types';

const OPENAI_DEFAULTS = PROVIDER_PRESETS['openai-compatible'];

const DEFAULT_CONFIG: AppConfig = {
  provider: {
    type: 'openai-compatible',
    apiKey: '',
    model: OPENAI_DEFAULTS.defaultModel,
    baseUrl: OPENAI_DEFAULTS.defaultBaseUrl
  },
  targetLanguage: 'Chinese',
  ui: {
    bubbleAutoHideMs: 6000,
    clipboardPollMs: 900,
    minCaptureLength: 2,
    maxCaptureLength: 6000
  }
};

interface StoreLike<T> {
  get<Key extends keyof T>(key: Key, defaultValue: T[Key]): T[Key];
  set(value: Partial<T>): void;
}

export class ConfigStore {
  private readonly store: StoreLike<AppConfig>;

  constructor() {
    this.store = new Store<AppConfig>({
      name: 'settings',
      defaults: DEFAULT_CONFIG
    }) as unknown as StoreLike<AppConfig>;
  }

  get(): AppConfig {
    return {
      provider: this.store.get('provider', DEFAULT_CONFIG.provider),
      targetLanguage: this.store.get('targetLanguage', DEFAULT_CONFIG.targetLanguage),
      ui: this.store.get('ui', DEFAULT_CONFIG.ui)
    };
  }

  update(payload: ConfigUpdatePayload): AppConfig {
    const current = this.get();
    const next: AppConfig = {
      ...current,
      targetLanguage: payload.targetLanguage ?? current.targetLanguage,
      provider: {
        ...current.provider,
        ...(payload.provider ?? {})
      },
      ui: {
        ...current.ui,
        ...(payload.ui ?? {})
      }
    };

    if (next.provider.baseUrl !== undefined) {
      const trimmedBaseUrl = next.provider.baseUrl.trim();
      next.provider.baseUrl = trimmedBaseUrl.length > 0 ? trimmedBaseUrl : undefined;
    }

    next.provider.apiKey = next.provider.apiKey.trim();
    next.provider.model = next.provider.model.trim();

    const providerPreset = PROVIDER_PRESETS[next.provider.type];
    if (!next.provider.model) {
      next.provider.model = providerPreset.defaultModel;
    }

    if (!next.provider.baseUrl && providerPreset.defaultBaseUrl) {
      next.provider.baseUrl = providerPreset.defaultBaseUrl;
    }

    next.targetLanguage = next.targetLanguage.trim() || 'Chinese';

    this.store.set(next);
    return next;
  }
}
