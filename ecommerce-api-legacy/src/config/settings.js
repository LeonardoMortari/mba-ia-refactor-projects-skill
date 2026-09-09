module.exports = {
  port: Number(process.env.PORT || 3000),
  databasePath: process.env.DATABASE_PATH || ':memory:',
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || ''
};
