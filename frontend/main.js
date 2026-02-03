const { app, BrowserWindow, dialog } = require('electron');
if (require('electron-squirrel-startup')) app.quit();

const path = require('path');
const { spawn } = require('child_process');
const http = require('http');
const kill = require('tree-kill');

let mainWindow = null;
let serverProc = null;

const SERVER_URL = 'http://127.0.0.1:8050';
const SERVER_START_TIMEOUT = 20_000;

function startServer() {
  const isPackaged = app.isPackaged;
  if (!isPackaged) {
    const pyCmd = process.platform === 'win32' ? 'python' : 'python3';
    const scriptPath = path.join(__dirname, '..', 'backend', 'app.py');
    console.log('Starting backend (dev mode):', pyCmd, scriptPath);
    serverProc = spawn(pyCmd, [scriptPath], {
      cwd: path.dirname(scriptPath),
      stdio: ['ignore', 'pipe', 'pipe'],
    });
  } else {
    let exe = path.join(process.resourcesPath, 'app', 'app');
    if (process.platform === 'win32') exe += '.exe';
    console.log('Starting backend (packaged):', exe);
    serverProc = spawn(exe, [], {
      cwd: path.dirname(exe),
      stdio: ['ignore', 'pipe', 'pipe'],
    });
  }

  if (!serverProc) throw new Error('Не удалось запустить серверный процесс.');

  serverProc.stdout.on('data', (b) => {
    process.stdout.write(`[backend stdout] ${b}`);
  });
  serverProc.stderr.on('data', (b) => {
    process.stderr.write(`[backend stderr] ${b}`);
  });
  serverProc.on('exit', (code, signal) => {
    console.log(`Backend exited (code=${code}, signal=${signal})`);
  });

  return serverProc;
}

function stopServer() {
  if (!serverProc || serverProc.killed) return;
  const pid = serverProc.pid;
  console.log('Stopping backend, pid=', pid);
  kill(pid, 'SIGTERM', (err) => {
    if (err) {
      console.warn('tree-kill error, trying direct kill:', err);
      try { process.kill(pid); } catch (e) { /* ignore */ }
    } else {
      console.log('Backend killed');
    }
  });
}

function waitForServer(url, timeoutMs = 10000, intervalMs = 250) {
  const start = Date.now();
  return new Promise((resolve, reject) => {
    (function poll() {
      if (Date.now() - start > timeoutMs) {
        return reject(new Error('Timeout waiting for server'));
      }
      const req = http.get(url, (res) => {
        res.resume();
        resolve();
      });
      req.on('error', () => {
        setTimeout(poll, intervalMs);
      });
    })();
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  mainWindow.on('close', (e) => {
    if (serverProc) {
      try {
        stopServer();
      } catch (er) {
        console.warn('Error stopping server on window close:', er);
      }
    }
  });

  mainWindow.loadURL(SERVER_URL);
}

app.whenReady().then(async () => {
  try {
    startServer();
    await waitForServer(SERVER_URL, SERVER_START_TIMEOUT);
    createWindow();
  } catch (err) {
    console.error('Failed to start backend or connect:', err);
    dialog.showErrorBox('Ошибка', `Не удалось запустить или подключиться к серверу: ${err.message}`);
    try { stopServer(); } catch (e) {}
    app.quit();
  }

  app.on('activate', () => {
    if (mainWindow === null) createWindow();
  });
});

app.on('before-quit', () => {
  if (serverProc) stopServer();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    if (serverProc) stopServer();
    app.quit();
  }
});