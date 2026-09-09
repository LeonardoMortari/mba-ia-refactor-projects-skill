function errorHandler(error, _req, res, _next) {
  console.error('Request failed:', error.message);
  return res.status(error.status || 500).send(error.status ? error.message : 'Erro interno do servidor');
}

module.exports = errorHandler;
