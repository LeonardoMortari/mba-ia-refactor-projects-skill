const sqlite3 = require('sqlite3').verbose();
const settings = require('../config/settings');

const db = new sqlite3.Database(settings.databasePath);

function run(sql, params = []) {
  return new Promise((resolve, reject) => db.run(sql, params, function onRun(error) {
    if (error) reject(error); else resolve({ lastID: this.lastID, changes: this.changes });
  }));
}

function get(sql, params = []) {
  return new Promise((resolve, reject) => db.get(sql, params, (error, row) => error ? reject(error) : resolve(row)));
}

function all(sql, params = []) {
  return new Promise((resolve, reject) => db.all(sql, params, (error, rows) => error ? reject(error) : resolve(rows)));
}

function exec(sql) {
  return new Promise((resolve, reject) => db.exec(sql, error => error ? reject(error) : resolve()));
}

async function initialize() {
  await exec(`
    PRAGMA foreign_keys = ON;
    CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, pass TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY, title TEXT NOT NULL, price REAL NOT NULL, active INTEGER NOT NULL DEFAULT 1);
    CREATE TABLE IF NOT EXISTS enrollments (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, course_id INTEGER NOT NULL, FOREIGN KEY(user_id) REFERENCES users(id), FOREIGN KEY(course_id) REFERENCES courses(id));
    CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER NOT NULL, amount REAL NOT NULL, status TEXT NOT NULL, FOREIGN KEY(enrollment_id) REFERENCES enrollments(id));
    CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY, action TEXT NOT NULL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP);
  `);
  if (!(await get('SELECT id FROM users LIMIT 1'))) {
    await run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', ['Leonan', 'leonan@fullcycle.com.br', 'development-only']);
    await run('INSERT INTO courses (title, price, active) VALUES (?, ?, ?), (?, ?, ?)', ['Clean Architecture', 997, 1, 'Docker', 497, 1]);
  }
}

module.exports = { db, run, get, all, exec, initialize };
