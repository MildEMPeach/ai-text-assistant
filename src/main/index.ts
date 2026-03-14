import { app, globalShortcut } from 'electron';

import type { SelectionPayload } from '../shared/types';
import { ConfigStore } from './config/store';
import { registerIpcHandlers } from './ipc';
import log from './logger';
import { SelectionMonitor } from './services/selection-monitor';
import { TaskOrchestrator } from './services/task-orchestrator';
import { AppTray } from './tray';
import { BubbleWindow } from './windows/bubble-window';
import { PanelWindow } from './windows/panel-window';

const SINGLE_INSTANCE_LOCK = app.requestSingleInstanceLock();
if (!SINGLE_INSTANCE_LOCK) {
  app.quit();
}

const configStore = new ConfigStore();
const taskOrchestrator = new TaskOrchestrator(configStore);
const selectionMonitor = new SelectionMonitor(configStore);
const panelWindow = new PanelWindow();
const bubbleWindow = new BubbleWindow();
const appTray = new AppTray();

let latestSelection: SelectionPayload | null = null;

const shortcut = process.platform === 'darwin' ? 'Command+Shift+L' : 'Control+Shift+L';

function shouldReuseSelection(payload: SelectionPayload | null): payload is SelectionPayload {
  if (!payload) {
    return false;
  }

  return Date.now() - payload.timestamp < 180000;
}

function openPanel(): void {
  if (shouldReuseSelection(latestSelection)) {
    panelWindow.show(latestSelection);
    return;
  }

  panelWindow.show();
}

function registerShortcuts(): void {
  const ok = globalShortcut.register(shortcut, () => {
    void selectionMonitor.triggerFromShortcut();
  });

  if (!ok) {
    log.warn(`Failed to register shortcut: ${shortcut}`);
  }
}

function setupSelectionFlow(): void {
  selectionMonitor.on('selection', (payload) => {
    latestSelection = payload;

    if (payload.source === 'shortcut') {
      bubbleWindow.hide();
      panelWindow.show(payload);
      return;
    }

    const autoHideMs = configStore.get().ui.bubbleAutoHideMs;
    bubbleWindow.showNear(payload.cursor, autoHideMs);
  });

  selectionMonitor.start();
}

async function bootstrap(): Promise<void> {
  panelWindow.create();
  bubbleWindow.create();

  appTray.create({
    openPanel,
    openSettings: openPanel,
    quit: () => app.quit()
  });

  registerIpcHandlers({
    configStore,
    taskOrchestrator,
    panelWindow,
    bubbleWindow,
    selectionMonitor,
    getLatestSelection: () => latestSelection
  });

  registerShortcuts();
  setupSelectionFlow();

  log.info('App started');
}

app.whenReady().then(() => {
  void bootstrap();
});

app.on('second-instance', () => {
  openPanel();
});

app.on('before-quit', () => {
  panelWindow.setAllowQuit(true);
  selectionMonitor.stop();
  globalShortcut.unregisterAll();
});

app.on('activate', () => {
  openPanel();
});

process.on('uncaughtException', (error) => {
  log.error('uncaughtException', error);
});

process.on('unhandledRejection', (reason) => {
  log.error('unhandledRejection', reason);
});
