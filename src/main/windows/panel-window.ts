import { BrowserWindow } from 'electron';
import { join } from 'node:path';

import { IPC_CHANNELS } from '../../shared/ipc';
import type { SelectionPayload } from '../../shared/types';
import { loadRendererPage } from './window-utils';

export class PanelWindow {
  private window: BrowserWindow | null = null;
  private isReady = false;
  private pendingSelection: SelectionPayload | null = null;
  private allowQuit = false;

  create(): BrowserWindow {
    if (this.window) {
      return this.window;
    }

    this.window = new BrowserWindow({
      width: 940,
      height: 700,
      minWidth: 780,
      minHeight: 600,
      show: false,
      backgroundColor: '#0d1a1f',
      title: 'AI Text Assistant',
      webPreferences: {
        preload: join(__dirname, '../../preload/index.js'),
        contextIsolation: true,
        nodeIntegration: false,
        sandbox: false
      }
    });

    this.window.webContents.on('did-finish-load', () => {
      this.isReady = true;
      if (this.pendingSelection) {
        this.sendSelection(this.pendingSelection);
        this.pendingSelection = null;
      }
    });

    this.window.on('close', (event) => {
      if (!this.allowQuit) {
        event.preventDefault();
        this.window?.hide();
      }
    });

    void loadRendererPage(this.window, 'panel.html');

    return this.window;
  }

  show(selection?: SelectionPayload): void {
    if (!this.window) {
      return;
    }

    if (selection) {
      this.injectSelection(selection);
    }

    if (!this.window.isVisible()) {
      this.window.show();
    }

    this.window.focus();
  }

  hide(): void {
    this.window?.hide();
  }

  setAllowQuit(allowQuit: boolean): void {
    this.allowQuit = allowQuit;
  }

  injectSelection(selection: SelectionPayload): void {
    if (!this.window) {
      return;
    }

    if (!this.isReady) {
      this.pendingSelection = selection;
      return;
    }

    this.sendSelection(selection);
  }

  private sendSelection(selection: SelectionPayload): void {
    this.window?.webContents.send(IPC_CHANNELS.PANEL_INJECT_TEXT, selection);
  }
}
