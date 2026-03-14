import { app, BrowserWindow } from 'electron';
import { join } from 'node:path';

import log from '../logger';

function getDevServerUrl(): string | null {
  const url = process.env.ELECTRON_RENDERER_URL?.trim();
  return url ? url.replace(/\/$/, '') : null;
}

export async function loadRendererPage(window: BrowserWindow, page: string): Promise<void> {
  const rendererFile = join(__dirname, '../../renderer', page);
  const devServerUrl = getDevServerUrl();

  if (app.isPackaged || !devServerUrl) {
    await window.loadFile(rendererFile);
    return;
  }

  try {
    await window.loadURL(`${devServerUrl}/${page}`);
  } catch (error) {
    log.warn(`Dev server unavailable, falling back to built renderer for ${page}`, error);
    await window.loadFile(rendererFile);
  }
}
