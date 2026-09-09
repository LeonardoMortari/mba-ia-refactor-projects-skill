const checkoutService = require('../services/checkout-service');
const repositories = require('../models/repositories');

async function checkout(req, res, next) {
  try {
    const body = req.body || {};
    const result = await checkoutService.checkout({ name: body.usr, email: body.eml, password: body.pwd, courseId: body.c_id, card: body.card });
    return res.status(200).json(result);
  } catch (error) { return next(error); }
}

async function financialReport(_req, res, next) {
  try { return res.json(await repositories.financialReport()); } catch (error) { return next(error); }
}

async function deleteUser(req, res, next) {
  try {
    const result = await repositories.deleteUser(req.params.id);
    if (!result.changes) return res.status(404).send('Usuário não encontrado');
    return res.send('Usuário deletado com sucesso.');
  } catch (error) { return next(error); }
}

module.exports = { checkout, financialReport, deleteUser };
