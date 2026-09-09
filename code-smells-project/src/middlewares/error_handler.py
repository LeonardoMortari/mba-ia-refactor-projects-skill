def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception("Unhandled application error: %s", error)
        return {"erro": "Erro interno do servidor"}, 500
