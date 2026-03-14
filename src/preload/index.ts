import { contextBridge, ipcRenderer } from 'electron';

import type { DesktopAPI } from '../shared/ipc';
import { IPC_CHANNELS } from '../shared/ipc';
import type { SelectionPayload } from '../shared/types';

const api: DesktopAPI = {
  runTask(request) {
    return ipcRenderer.invoke(IPC_CHANNELS.RUN_TASK, request);
  },
  getConfig() {
    return ipcRenderer.invoke(IPC_CHANNELS.GET_CONFIG);
  },
  updateConfig(payload) {
    return ipcRenderer.invoke(IPC_CHANNELS.UPDATE_CONFIG, payload);
  },
  copyText(text) {
    return ipcRenderer.invoke(IPC_CHANNELS.COPY_TEXT, text);
  },
  openPanelFromBubble() {
    ipcRenderer.send(IPC_CHANNELS.BUBBLE_OPEN_PANEL);
  },
  onInjectText(callback) {
    const listener = (_event: Electron.IpcRendererEvent, payload: SelectionPayload) => {
      callback(payload);
    };

    ipcRenderer.on(IPC_CHANNELS.PANEL_INJECT_TEXT, listener);
    return () => {
      ipcRenderer.off(IPC_CHANNELS.PANEL_INJECT_TEXT, listener);
    };
  },
  onPanelError(callback) {
    const listener = (_event: Electron.IpcRendererEvent, message: string) => {
      callback(message);
    };

    ipcRenderer.on(IPC_CHANNELS.PANEL_ERROR, listener);
    return () => {
      ipcRenderer.off(IPC_CHANNELS.PANEL_ERROR, listener);
    };
  }
};

contextBridge.exposeInMainWorld('api', api);
