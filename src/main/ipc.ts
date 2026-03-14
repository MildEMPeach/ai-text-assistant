import { clipboard, ipcMain } from 'electron';
import { z } from 'zod';

import { IPC_CHANNELS } from '../shared/ipc';
import type { SelectionPayload, TaskAction } from '../shared/types';
import type { ConfigStore } from './config/store';
import log from './logger';
import type { SelectionMonitor } from './services/selection-monitor';
import type { TaskOrchestrator } from './services/task-orchestrator';
import type { BubbleWindow } from './windows/bubble-window';
import type { PanelWindow } from './windows/panel-window';

const taskRequestSchema = z.object({
  action: z.enum(['summarize', 'translate', 'custom']),
  text: z.string().min(1).max(10000),
  customPrompt: z.string().max(2000).optional(),
  targetLanguage: z.string().max(64).optional()
});

const configUpdateSchema = z
  .object({
    provider: z
      .object({
        type: z.enum(['openai-compatible', 'anthropic', 'gemini', 'deepseek']).optional(),
        apiKey: z.string().max(512).optional(),
        model: z.string().max(128).optional(),
        baseUrl: z.string().max(256).optional()
      })
      .optional(),
    targetLanguage: z.string().max(64).optional(),
    ui: z
      .object({
        bubbleAutoHideMs: z.number().int().min(1000).max(20000).optional(),
        clipboardPollMs: z.number().int().min(300).max(5000).optional(),
        minCaptureLength: z.number().int().min(1).max(200).optional(),
        maxCaptureLength: z.number().int().min(10).max(20000).optional()
      })
      .optional()
  })
  .strict();

interface IPCRegistrationDeps {
  configStore: ConfigStore;
  taskOrchestrator: TaskOrchestrator;
  panelWindow: PanelWindow;
  bubbleWindow: BubbleWindow;
  selectionMonitor: SelectionMonitor;
  getLatestSelection: () => SelectionPayload | null;
}

function toUserErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  return 'Unknown error';
}

export function registerIpcHandlers(deps: IPCRegistrationDeps): void {
  ipcMain.removeHandler(IPC_CHANNELS.GET_CONFIG);
  ipcMain.removeHandler(IPC_CHANNELS.UPDATE_CONFIG);
  ipcMain.removeHandler(IPC_CHANNELS.RUN_TASK);
  ipcMain.removeHandler(IPC_CHANNELS.COPY_TEXT);
  ipcMain.removeAllListeners(IPC_CHANNELS.BUBBLE_OPEN_PANEL);

  ipcMain.handle(IPC_CHANNELS.GET_CONFIG, () => deps.configStore.get());

  ipcMain.handle(IPC_CHANNELS.UPDATE_CONFIG, (_event, payload: unknown) => {
    const parsed = configUpdateSchema.parse(payload);
    const updated = deps.configStore.update(parsed);
    return updated;
  });

  ipcMain.handle(IPC_CHANNELS.RUN_TASK, async (_event, payload: unknown) => {
    const parsed = taskRequestSchema.parse(payload);
    const taskPayload: {
      action: TaskAction;
      text: string;
      customPrompt?: string;
      targetLanguage?: string;
    } = parsed;

    try {
      return await deps.taskOrchestrator.run(taskPayload);
    } catch (error) {
      log.error('Task execution failed', error);
      throw new Error(toUserErrorMessage(error));
    }
  });

  ipcMain.handle(IPC_CHANNELS.COPY_TEXT, (_event, text: unknown) => {
    const safeText = z.string().max(20000).parse(text);
    clipboard.writeText(safeText);
    deps.selectionMonitor.ignoreNextText(safeText);
  });

  ipcMain.on(IPC_CHANNELS.BUBBLE_OPEN_PANEL, () => {
    deps.bubbleWindow.hide();
    const latest = deps.getLatestSelection();
    deps.panelWindow.show(latest || undefined);
  });
}
