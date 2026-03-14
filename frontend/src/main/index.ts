/**
 * Electron main process for RuneLoLDB.
 *
 * Responsibilities:
 * - Create the browser window overlay.
 * - Poll the League Client API to detect champion select.
 * - Communicate with the backend API for rune recommendations.
 * - Handle IPC calls from the renderer to import rune pages.
 */

import { app, BrowserWindow, ipcMain, shell } from 'electron';
import * as path from 'path';
import { LeagueClientPoller } from './leagueClientPoller';
import { BackendClient } from './backendClient';
import { RecommendRequest, RunePage } from '../shared/types';

const isDev = process.argv.includes('--dev');
const BACKEND_URL = process.env.BACKEND_URL ?? 'http://localhost:8000';

let mainWindow: BrowserWindow | null = null;
let poller: LeagueClientPoller | null = null;

// ---------------------------------------------------------------------------
// Window creation
// ---------------------------------------------------------------------------

function createWindow(): void {
  mainWindow = new BrowserWindow({
    width: 420,
    height: 620,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    resizable: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  if (isDev) {
    mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'));
    mainWindow.webContents.openDevTools({ mode: 'detach' });
  } else {
    mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'));
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// ---------------------------------------------------------------------------
// App lifecycle
// ---------------------------------------------------------------------------

app.whenReady().then(() => {
  createWindow();
  startPolling();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
  poller?.stop();
});

// ---------------------------------------------------------------------------
// League Client polling
// ---------------------------------------------------------------------------

function startPolling(): void {
  const backend = new BackendClient(BACKEND_URL);

  poller = new LeagueClientPoller({
    onChampSelectEntered: async (session) => {
      if (!mainWindow) return;

      const localCell = session.localPlayerCellId;
      const localPlayer = session.myTeam.find((p) => p.cellId === localCell);
      if (!localPlayer?.championId) return;

      // Identify the first locked enemy champion
      const enemyChampion = session.theirTeam.find((p) => p.championId > 0);
      if (!enemyChampion?.championId) return;

      const role =
        localPlayer.assignedPosition?.toUpperCase() || 'ANY';

      try {
        const req: RecommendRequest = {
          player_id: 'local-player',
          champion_id: localPlayer.championId,
          enemy_champion_id: enemyChampion.championId,
          role,
        };
        const recommendation = await backend.getRecommendation(req);
        mainWindow.webContents.send('recommendation-result', recommendation);
      } catch (err) {
        mainWindow.webContents.send('error', String(err));
      }
    },
    onChampSelectExited: () => {
      mainWindow?.webContents.send('champ-select-update', null);
    },
  });

  poller.start();
}

// ---------------------------------------------------------------------------
// IPC handlers
// ---------------------------------------------------------------------------

ipcMain.handle(
  'import-runes',
  async (_event, runePage: RunePage): Promise<{ success: boolean }> => {
    // TODO: Forward the rune page to the LCU via the backend or a direct call.
    // For now we log and return success so the renderer can be tested.
    console.log('[IPC] import-runes requested:', JSON.stringify(runePage, null, 2));
    return { success: true };
  },
);
