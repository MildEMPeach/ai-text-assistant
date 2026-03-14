import type { DesktopAPI } from '../shared/ipc';

declare global {
  interface Window {
    api: DesktopAPI;
  }
}

export {};
