import type { TaskRequest, TaskResult } from '../../shared/types';
import { ConfigStore } from '../config/store';
import { createProvider } from '../providers/provider-factory';

export class TaskOrchestrator {
  constructor(private readonly configStore: ConfigStore) {}

  async run(request: TaskRequest): Promise<TaskResult> {
    const config = this.configStore.get();
    const provider = createProvider(config.provider);
    const startedAt = Date.now();

    let output = '';
    if (request.action === 'summarize') {
      output = await provider.summarize(request.text);
    } else if (request.action === 'translate') {
      output = await provider.translate(request.text, request.targetLanguage || config.targetLanguage);
    } else {
      output = await provider.custom(request.text, request.customPrompt || 'Refine the text.');
    }

    return {
      action: request.action,
      output,
      model: config.provider.model,
      provider: config.provider.type,
      latencyMs: Date.now() - startedAt
    };
  }
}
