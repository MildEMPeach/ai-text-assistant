import { app, BrowserWindow } from 'electron';
import { join } from 'node:path';

const DEV_SERVER_URL = 'http://localhost:5173';

export async function loadRendererPage(window: BrowserWindow, page: string): Promise<void> {
  if (!app.isPackaged) {
    await window.loadURL(`${DEV_SERVER_URL}/${page}`);
    return;
  }

  await window.loadFile(join(__dirname, '../../renderer', page));
}
