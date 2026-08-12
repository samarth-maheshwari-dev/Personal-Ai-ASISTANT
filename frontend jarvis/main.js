const { app, BrowserWindow, globalShortcut } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let backendProcess = null;
let ollamaProcess = null;
let mainWindow = null;

function startOllama() {
    const ollamaPath = 'C:\\Users\\ASUS\\AppData\\Local\\Programs\\Ollama\\ollama.exe';
    ollamaProcess = spawn(ollamaPath, ['serve'], {
        detached: true,
        stdio: 'ignore',
        windowsHide: true
    });
    if (ollamaProcess) ollamaProcess.unref();
}

function startBackend() {
    startOllama();
    const rootDir = path.join(__dirname, '..');
    const pythonScript = path.join(rootDir, 'server.py');
    const venvPython = path.join(rootDir, '.venv', 'Scripts', 'python.exe');
    const pythonExecutable = require('fs').existsSync(venvPython) ? venvPython : 'python';

    backendProcess = spawn(pythonExecutable, [pythonScript], {
        cwd: rootDir,
        detached: true,
        stdio: 'ignore',
        windowsHide: true
    });
    if (backendProcess) backendProcess.unref();
}

// Enable Chromium permission flags for microphone recording
app.commandLine.appendSwitch('enable-speech-dispatcher');
app.commandLine.appendSwitch('use-fake-ui-for-media-stream');

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        title: "JARVIS AI Assistant",
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
        },
    });

    // Grant media permissions automatically in Electron
    mainWindow.webContents.session.setPermissionCheckHandler((webContents, permission) => {
        if (permission === 'media') return true;
        return true;
    });

    mainWindow.webContents.session.setPermissionRequestHandler((webContents, permission, callback) => {
        callback(true);
    });

    if (process.env.ELECTRON_START_URL) {
        mainWindow.loadURL(process.env.ELECTRON_START_URL);
    } else {
        mainWindow.loadFile(path.join(__dirname, 'dist', 'index.html'));
    }
}

app.whenReady().then(() => {
    startBackend();
    createWindow();

    // Register Global Hotkey Ctrl+Alt+J to bring JARVIS to focus anywhere
    globalShortcut.register('CommandOrControl+Alt+J', () => {
        if (mainWindow) {
            if (mainWindow.isVisible() && !mainWindow.isMinimized()) {
                mainWindow.minimize();
            } else {
                mainWindow.show();
                mainWindow.restore();
                mainWindow.focus();
            }
        }
    });

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
});

app.on('will-quit', () => {
    globalShortcut.unregisterAll();
});

app.on('window-all-closed', () => {
    if (backendProcess) backendProcess.kill();
    if (process.platform !== 'darwin') app.quit();
});

