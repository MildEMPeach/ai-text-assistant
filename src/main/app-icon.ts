import { app, nativeImage } from 'electron';
import { existsSync } from 'node:fs';
import { join } from 'node:path';

function getAssetPath(fileName: string): string {
  return join(app.getAppPath(), 'assets', fileName);
}

function getIconFileName(): string {
  return process.platform === 'win32' ? 'icon.ico' : 'icon.png';
}

export function getAppIconPath(): string | null {
  const iconPath = getAssetPath(getIconFileName());
  return existsSync(iconPath) ? iconPath : null;
}

export function loadAppIcon(): Electron.NativeImage {
  const iconPath = getAppIconPath();
  if (!iconPath) {
    return nativeImage.createEmpty();
  }

  return nativeImage.createFromPath(iconPath);
}
