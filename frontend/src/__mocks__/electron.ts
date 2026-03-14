/** Minimal Electron mock for Jest tests. */

export const app = {
  whenReady: jest.fn(() => Promise.resolve()),
  on: jest.fn(),
  quit: jest.fn(),
};

export const BrowserWindow = jest.fn().mockImplementation(() => ({
  loadFile: jest.fn(),
  on: jest.fn(),
  webContents: {
    send: jest.fn(),
    openDevTools: jest.fn(),
  },
  getAllWindows: jest.fn(() => []),
}));

BrowserWindow.getAllWindows = jest.fn(() => []);

export const ipcMain = {
  handle: jest.fn(),
  on: jest.fn(),
};

export const ipcRenderer = {
  on: jest.fn(),
  invoke: jest.fn(),
  removeAllListeners: jest.fn(),
};

export const contextBridge = {
  exposeInMainWorld: jest.fn(),
};

export const shell = {
  openExternal: jest.fn(),
};
