import type { AppConfig, TaskAction, TaskRequest } from '../shared/types';
import { PROVIDER_PRESETS } from '../shared/provider-presets';

const sourceText = document.querySelector<HTMLTextAreaElement>('#sourceText');
const customPrompt = document.querySelector<HTMLTextAreaElement>('#customPrompt');
const resultOutput = document.querySelector<HTMLElement>('#resultOutput');
const resultMeta = document.querySelector<HTMLElement>('#resultMeta');
const statusText = document.querySelector<HTMLElement>('#statusText');
const copyBtn = document.querySelector<HTMLButtonElement>('#copyBtn');
const settingsForm = document.querySelector<HTMLFormElement>('#settingsForm');

const providerType = document.querySelector<HTMLSelectElement>('#providerType');
const modelName = document.querySelector<HTMLInputElement>('#modelName');
const apiKey = document.querySelector<HTMLInputElement>('#apiKey');
const baseUrl = document.querySelector<HTMLInputElement>('#baseUrl');
const targetLanguage = document.querySelector<HTMLInputElement>('#targetLanguage');

const actionButtons = Array.from(document.querySelectorAll<HTMLButtonElement>('button[data-action]'));

let isLoading = false;
let currentConfig: AppConfig | null = null;

function assertElement<T>(element: T | null, selector: string): T {
  if (!element) {
    throw new Error(`Missing DOM element: ${selector}`);
  }
  return element;
}

function setStatus(message: string, mode: 'idle' | 'busy' | 'error' = 'idle'): void {
  const status = assertElement(statusText, '#statusText');
  status.textContent = message;
  status.classList.remove('is-busy', 'is-error');
  if (mode === 'busy') {
    status.classList.add('is-busy');
  }
  if (mode === 'error') {
    status.classList.add('is-error');
  }
}

function setLoadingState(next: boolean): void {
  isLoading = next;
  for (const button of actionButtons) {
    button.disabled = next;
  }

  const saveButton = document.querySelector<HTMLButtonElement>('#saveSettings');
  if (saveButton) {
    saveButton.disabled = next;
  }

  if (copyBtn) {
    copyBtn.disabled = next;
  }
}

function getSelectedProviderType(): AppConfig['provider']['type'] {
  return assertElement(providerType, '#providerType').value as AppConfig['provider']['type'];
}

function refreshProviderHints(forceValueUpdate: boolean): void {
  const selectedType = getSelectedProviderType();
  const preset = PROVIDER_PRESETS[selectedType];
  const modelInput = assertElement(modelName, '#modelName');
  const baseUrlInput = assertElement(baseUrl, '#baseUrl');

  modelInput.placeholder = preset.defaultModel;
  if (forceValueUpdate || !modelInput.value.trim()) {
    modelInput.value = preset.defaultModel;
  }

  if (preset.defaultBaseUrl) {
    baseUrlInput.placeholder = preset.defaultBaseUrl;
    if (forceValueUpdate || !baseUrlInput.value.trim()) {
      baseUrlInput.value = preset.defaultBaseUrl;
    }
  } else {
    baseUrlInput.placeholder = 'Provider 默认地址（可选）';
    if (forceValueUpdate) {
      baseUrlInput.value = '';
    }
  }
}

function applyConfig(config: AppConfig): void {
  assertElement(providerType, '#providerType').value = config.provider.type;
  assertElement(modelName, '#modelName').value = config.provider.model;
  assertElement(apiKey, '#apiKey').value = config.provider.apiKey;
  assertElement(baseUrl, '#baseUrl').value = config.provider.baseUrl || '';
  assertElement(targetLanguage, '#targetLanguage').value = config.targetLanguage;
  refreshProviderHints(false);
}

function readTaskInput(action: TaskAction): TaskRequest {
  const text = assertElement(sourceText, '#sourceText').value.trim();
  if (!text) {
    throw new Error('请输入或注入待处理文本。');
  }

  const request: TaskRequest = {
    action,
    text,
    targetLanguage: assertElement(targetLanguage, '#targetLanguage').value.trim() || undefined
  };

  if (action === 'custom') {
    const prompt = assertElement(customPrompt, '#customPrompt').value.trim();
    if (!prompt) {
      throw new Error('自定义模式需要填写提示词。');
    }
    request.customPrompt = prompt;
  }

  return request;
}

async function runTask(action: TaskAction): Promise<void> {
  if (isLoading) {
    return;
  }

  try {
    const request = readTaskInput(action);
    setLoadingState(true);
    setStatus('处理中...', 'busy');

    const result = await window.api.runTask(request);
    assertElement(resultOutput, '#resultOutput').textContent = result.output;
    assertElement(resultMeta, '#resultMeta').textContent = `provider=${result.provider} · model=${result.model} · ${result.latencyMs}ms`;
    setStatus('执行完成');
  } catch (error) {
    const message = error instanceof Error ? error.message : '执行失败';
    setStatus(message, 'error');
  } finally {
    setLoadingState(false);
  }
}

async function saveSettings(event: Event): Promise<void> {
  event.preventDefault();

  try {
    setLoadingState(true);
    setStatus('保存设置中...', 'busy');

    const updated = await window.api.updateConfig({
      provider: {
        type: getSelectedProviderType(),
        model: assertElement(modelName, '#modelName').value,
        apiKey: assertElement(apiKey, '#apiKey').value,
        baseUrl: assertElement(baseUrl, '#baseUrl').value
      },
      targetLanguage: assertElement(targetLanguage, '#targetLanguage').value
    });

    currentConfig = updated;
    applyConfig(updated);
    setStatus('设置已保存');
  } catch (error) {
    const message = error instanceof Error ? error.message : '设置保存失败';
    setStatus(message, 'error');
  } finally {
    setLoadingState(false);
  }
}

async function loadConfig(): Promise<void> {
  try {
    const config = await window.api.getConfig();
    currentConfig = config;
    applyConfig(config);
  } catch (error) {
    const message = error instanceof Error ? error.message : '读取配置失败';
    setStatus(message, 'error');
  }
}

function bindEvents(): void {
  for (const button of actionButtons) {
    const action = button.dataset.action as TaskAction;
    button.addEventListener('click', () => {
      void runTask(action);
    });
  }

  assertElement(copyBtn, '#copyBtn').addEventListener('click', async () => {
    const text = assertElement(resultOutput, '#resultOutput').textContent || '';
    if (!text || text === '等待执行...') {
      setStatus('暂无可复制结果', 'error');
      return;
    }

    await window.api.copyText(text);
    setStatus('结果已复制');
  });

  assertElement(settingsForm, '#settingsForm').addEventListener('submit', (event) => {
    void saveSettings(event);
  });

  assertElement(providerType, '#providerType').addEventListener('change', () => {
    refreshProviderHints(true);
  });

  window.api.onInjectText((payload) => {
    assertElement(sourceText, '#sourceText').value = payload.text;
    setStatus(payload.source === 'shortcut' ? '已通过快捷键注入文本' : '检测到新文本');
  });

  window.api.onPanelError((message) => {
    setStatus(message, 'error');
  });
}

void loadConfig().then(() => {
  bindEvents();
  refreshProviderHints(false);
  setStatus('就绪');
  if (currentConfig) {
    assertElement(resultMeta, '#resultMeta').textContent = `provider=${currentConfig.provider.type} · model=${currentConfig.provider.model}`;
  }
});
