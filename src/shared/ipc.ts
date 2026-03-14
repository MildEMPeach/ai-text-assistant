import type {
  AppConfig,
  ConfigUpdatePayload,
  SelectionPayload,
  TaskRequest,
  TaskResult
} from './types';

export const IPC_CHANNELS = {
  RUN_TASK: 'panel:run-task',
  GET_CONFIG: 'panel:get-config',
  UPDATE_CONFIG: 'panel:update-config',
  COPY_TEXT: 'panel:copy-text',
  BUBBLE_OPEN_PANEL: 'bubble:open-panel',
  PANEL_INJECT_TEXT: 'panel:inject-text',
  PANEL_ERROR: 'panel:error'
} as const;

export interface DesktopAPI {
  runTask(request: TaskRequest): Promise<TaskResult>;
  getConfig(): Promise<AppConfig>;
  updateConfig(payload: ConfigUpdatePayload): Promise<AppConfig>;
  copyText(text: string): Promise<void>;
  openPanelFromBubble(): void;
  onInjectText(callback: (payload: SelectionPayload) => void): () => void;
  onPanelError(callback: (message: string) => void): () => void;
}
