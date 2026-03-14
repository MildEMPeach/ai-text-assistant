import { BrowserWindow, screen } from 'electron';
import { join } from 'node:path';

import { loadRendererPage } from './window-utils';

export class BubbleWindow {
  private window: BrowserWindow | null = null;
  private hideTimer: NodeJS.Timeout | null = null;

  create(): BrowserWindow {
    if (this.window) {
      return this.window;
    }

    this.window = new BrowserWindow({
      width: 56,
      height: 56,
      show: false,
      frame: false,
      transparent: true,
      alwaysOnTop: true,
      skipTaskbar: true,
      focusable: false,
      movable: false,
      resizable: false,
      hasShadow: false,
      webPreferences: {
        preload: join(__dirname, '../../preload/index.js'),
        contextIsolation: true,
        nodeIntegration: false,
        sandbox: false
      }
    });

    this.window.setVisibleOnAllWorkspaces(true, {
      visibleOnFullScreen: true
    });

    void loadRendererPage(this.window, 'bubble.html');
    return this.window;
  }

  showNear(cursor: { x: number; y: number }, autoHideMs: number): void {
    if (!this.window) {
      return;
    }

    const display = screen.getDisplayNearestPoint(cursor);
    const bubbleBounds = this.window.getBounds();

    const x = Math.min(
      Math.max(cursor.x + 14, display.workArea.x),
      display.workArea.x + display.workArea.width - bubbleBounds.width
    );

    const y = Math.min(
      Math.max(cursor.y + 14, display.workArea.y),
      display.workArea.y + display.workArea.height - bubbleBounds.height
    );

    this.window.setPosition(x, y, false);
    this.window.showInactive();

    this.resetHideTimer(autoHideMs);
  }

  hide(): void {
    if (this.hideTimer) {
      clearTimeout(this.hideTimer);
      this.hideTimer = null;
    }

    this.window?.hide();
  }

  private resetHideTimer(ms: number): void {
    if (this.hideTimer) {
      clearTimeout(this.hideTimer);
    }

    this.hideTimer = setTimeout(() => {
      this.window?.hide();
    }, Math.max(1200, ms));
  }
}
