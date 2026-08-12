const express = require('express');
const cors = require('cors');
const path = require('path');
const db = require('./db');

const app = express();
app.use(cors());
app.use(express.json());

// Simple health check
app.get('/api/health', (req, res) => {
    res.json({ status: 'ok' });
});

// Echo command endpoint – you can replace with real logic later
app.post('/api/command', (req, res) => {
    const { input } = req.body;
    // Store command in DB (optional)
    db.run('INSERT INTO commands (input, timestamp) VALUES (?, datetime("now"))', [input], (err) => {
        if (err) console.error('DB insert error', err);
    });
    res.json({ message: `You said: ${input}`, type: 'chat', success: true, timestamp: new Date().toISOString() });
});

// Serve static files in production (Electron will load from dist)
app.use(express.static(path.join(__dirname, '..', 'dist')));

const PORT = process.env.PORT || 3000;
const server = app.listen(PORT, () => {
    console.log(`Backend listening on http://localhost:${PORT}`);
});

server.on('error', (err) => {
    if (err.code === 'EADDRINUSE') {
        console.log(`Port ${PORT} is already in use, assuming backend is running.`);
    } else {
        console.error('Server error:', err);
    }
});

