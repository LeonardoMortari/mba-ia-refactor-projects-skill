const database = require('../database/connection');

async function findCourse(id) { return database.get('SELECT * FROM courses WHERE id = ? AND active = 1', [id]); }
async function findUserByEmail(email) { return database.get('SELECT * FROM users WHERE email = ?', [email]); }
async function createUser(name, email, pass) { return database.run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [name, email, pass]); }

async function createEnrollment(userId, courseId) { return database.run('INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)', [userId, courseId]); }
async function createPayment(enrollmentId, amount, status) { return database.run('INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)', [enrollmentId, amount, status]); }
async function createAuditLog(action) { return database.run('INSERT INTO audit_logs (action) VALUES (?)', [action]); }

async function financialReport() {
  return database.all(`SELECT c.title AS course, COALESCE(SUM(CASE WHEN p.status = 'PAID' THEN p.amount ELSE 0 END), 0) AS revenue, COUNT(DISTINCT e.user_id) AS students
    FROM courses c LEFT JOIN enrollments e ON e.course_id = c.id LEFT JOIN payments p ON p.enrollment_id = e.id GROUP BY c.id, c.title ORDER BY c.id`);
}

async function deleteUser(userId) {
  const user = await database.get('SELECT id FROM users WHERE id = ?', [userId]);
  if (!user) return { changes: 0 };
  await database.run('DELETE FROM payments WHERE enrollment_id IN (SELECT id FROM enrollments WHERE user_id = ?)', [userId]);
  await database.run('DELETE FROM enrollments WHERE user_id = ?', [userId]);
  return database.run('DELETE FROM users WHERE id = ?', [userId]);
}

module.exports = { findCourse, findUserByEmail, createUser, createEnrollment, createPayment, createAuditLog, financialReport, deleteUser };
