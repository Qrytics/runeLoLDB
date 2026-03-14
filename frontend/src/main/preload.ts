/**
 * Electron preload script.
 *
 * Exposes a safe, typed API surface to the renderer via contextBridge.
 * No Node.js globals are exposed directly.
 */

import { contextBridge, ipcRenderer } from 'electron';
import { RecommendResponse, RunePage } from '../shared/types';

contextBridge.exposeInMainWorld('runeAPI', {
  /** Listen for recommendation results pushed from the main process. */
  onRecommendation: (
    callback: (recommendation: RecommendResponse) => void,
  ): void => {
    ipcRenderer.on('recommendation-result', (_event, data) => callback(data));
  },

  /** Listen for champ-select session updates (null = exited). */
  onChampSelectUpdate: (
    callback: (session: unknown) => void,
  ): void => {
    ipcRenderer.on('champ-select-update', (_event, data) => callback(data));
  },

  /** Listen for error messages from the main process. */
  onError: (callback: (message: string) => void): void => {
    ipcRenderer.on('error', (_event, msg) => callback(msg));
  },

  /** Ask the main process to import the given rune page into the LoL client. */
  importRunes: (runePage: RunePage): Promise<{ success: boolean }> =>
    ipcRenderer.invoke('import-runes', runePage),

  /** Remove all listeners added by this API (call on unmount). */
  removeAllListeners: (): void => {
    ipcRenderer.removeAllListeners('recommendation-result');
    ipcRenderer.removeAllListeners('champ-select-update');
    ipcRenderer.removeAllListeners('error');
  },
});
