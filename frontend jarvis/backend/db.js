const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const dbPath = path.resolve(__dirname, 'jarvis.db');
const db = new sqlite3.Database(dbPath, (err) => {
    if (err) {
        console.error('Failed to open DB', err);
    } else {
        console.log('Connected to SQLite DB at', dbPath);
        // Initialize table if not exists
        db.run(`CREATE TABLE IF NOT EXISTS commands (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      input TEXT NOT NULL,
      timestamp TEXT NOT NULL
    )`);
    }
});

module.exports = db;
