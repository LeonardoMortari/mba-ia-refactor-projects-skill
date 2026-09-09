const database = require('../database/connection');
const repositories = require('../models/repositories');

function paymentStatus(card) { return String(card).startsWith('4') ? 'PAID' : 'DENIED'; }

async function checkout({ name, email, password, courseId, card }) {
  if (!name || !email || !courseId || !card) throw Object.assign(new Error('Bad Request'), { status: 400 });
  const course = await repositories.findCourse(courseId);
  if (!course) throw Object.assign(new Error('Curso não encontrado'), { status: 404 });
  const status = paymentStatus(card);
  if (status === 'DENIED') throw Object.assign(new Error('Pagamento recusado'), { status: 400 });

  await database.exec('BEGIN');
  try {
    let user = await repositories.findUserByEmail(email);
    let userId = user && user.id;
    if (!user) userId = (await repositories.createUser(name, email, password || 'development-only')).lastID;
    const enrollment = await repositories.createEnrollment(userId, courseId);
    await repositories.createPayment(enrollment.lastID, course.price, status);
    await repositories.createAuditLog(`Checkout course ${courseId} by user ${userId}`);
    await database.exec('COMMIT');
    return { msg: 'Sucesso', enrollment_id: enrollment.lastID };
  } catch (error) {
    await database.exec('ROLLBACK');
    throw error;
  }
}

module.exports = { checkout };
