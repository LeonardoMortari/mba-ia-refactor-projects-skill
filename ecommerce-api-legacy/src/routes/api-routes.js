const express = require('express');
const controller = require('../controllers/api-controller');

const router = express.Router();
router.post('/checkout', controller.checkout);
router.get('/admin/financial-report', controller.financialReport);
router.delete('/users/:id', controller.deleteUser);

module.exports = router;
