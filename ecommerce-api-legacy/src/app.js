const express = require('express');
const settings = require('./config/settings');
const database = require('./database/connection');
const apiRoutes = require('./routes/api-routes');
const errorHandler = require('./middlewares/error-handler');

async function createApp() {
  await database.initialize();
  const app = express();
  app.use(express.json());
  app.use('/api', apiRoutes);
  app.use(errorHandler);
  return app;
}

if (require.main === module) {
  createApp().then(app => app.listen(settings.port, () => console.log(`LMS API rodando na porta ${settings.port}`))).catch(error => { console.error(error); process.exitCode = 1; });
}

module.exports = { createApp };
