import { Menu, Tray, nativeImage } from 'electron';

import { loadAppIcon } from './app-icon';

function createFallbackTrayIcon() {
  const svg = `
  <svg width="64" height="64" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#1A8A8E" />
        <stop offset="100%" stop-color="#C87A2B" />
      </linearGradient>
    </defs>
    <rect x="6" y="6" width="52" height="52" rx="16" fill="url(#g)"/>
    <path d="M32 16L36 28L48 32L36 36L32 48L28 36L16 32L28 28L32 16Z" fill="#FDFCF7"/>
  </svg>`;

  const dataUrl = `data:image/svg+xml;base64,${Buffer.from(svg).toString('base64')}`;
  return nativeImage.createFromDataURL(dataUrl).resize({ width: 18, height: 18 });
}

function createTrayIcon() {
  const icon = loadAppIcon();
  if (!icon.isEmpty()) {
    return icon.resize({ width: 18, height: 18 });
  }

  return createFallbackTrayIcon();
}

export class AppTray {
  private tray: Tray | null = null;

  create(actions: { openPanel: () => void; openSettings: () => void; quit: () => void }): Tray {
    if (this.tray) {
      return this.tray;
    }

    this.tray = new Tray(createTrayIcon());
    this.tray.setToolTip('AI Text Assistant');
    this.tray.setContextMenu(
      Menu.buildFromTemplate([
        { label: '打开面板', click: actions.openPanel },
        { label: '设置', click: actions.openSettings },
        { type: 'separator' },
        { label: '退出', click: actions.quit }
      ])
    );

    this.tray.on('double-click', actions.openPanel);

    return this.tray;
  }
}
