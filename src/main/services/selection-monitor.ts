import { clipboard, screen } from 'electron';
import { EventEmitter } from 'node:events';

import type { SelectionPayload } from '../../shared/types';
import { ConfigStore } from '../config/store';

export class SelectionMonitor extends EventEmitter {
  private timer: NodeJS.Timeout | null = null;
  private lastText = '';
  private checking = false;
  private readonly ignoredTexts = new Set<string>();

  constructor(private readonly configStore: ConfigStore) {
    super();
  }

  override on(eventName: 'selection', listener: (payload: SelectionPayload) => void): this {
    return super.on(eventName, listener);
  }

  start(): void {
    this.stop();
    this.lastText = this.readClipboardText();
    const interval = Math.max(300, this.configStore.get().ui.clipboardPollMs);
    this.timer = setInterval(() => {
      void this.pollClipboard();
    }, interval);
  }

  stop(): void {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
  }

  ignoreNextText(text: string): void {
    const normalized = text.trim();
    if (normalized) {
      this.ignoredTexts.add(normalized);
    }
  }

  async triggerFromShortcut(): Promise<void> {
    const text = this.readClipboardText();
    if (!this.shouldCapture(text)) {
      return;
    }

    this.lastText = text;
    this.emitSelection(text, 'shortcut');
  }

  private async pollClipboard(): Promise<void> {
    if (this.checking) {
      return;
    }
    this.checking = true;

    try {
      const text = this.readClipboardText();
      if (!this.shouldCapture(text)) {
        return;
      }

      if (text === this.lastText) {
        return;
      }

      if (this.ignoredTexts.has(text)) {
        this.ignoredTexts.delete(text);
        this.lastText = text;
        return;
      }

      this.lastText = text;
      this.emitSelection(text, 'clipboard');
    } finally {
      this.checking = false;
    }
  }

  private shouldCapture(text: string): boolean {
    if (!text) {
      return false;
    }

    const { minCaptureLength, maxCaptureLength } = this.configStore.get().ui;
    return text.length >= minCaptureLength && text.length <= maxCaptureLength;
  }

  private emitSelection(text: string, source: SelectionPayload['source']): void {
    const cursor = screen.getCursorScreenPoint();
    const payload: SelectionPayload = {
      text,
      source,
      cursor,
      timestamp: Date.now()
    };

    this.emit('selection', payload);
  }

  private readClipboardText(): string {
    return clipboard.readText().trim();
  }
}
