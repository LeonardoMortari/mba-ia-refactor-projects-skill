from flask import Blueprint, jsonify
from src.controllers import api

bp = Blueprint("api", __name__)
bp.add_url_rule("/produtos", view_func=api.list_products, methods=["GET"])
bp.add_url_rule("/produtos/busca", view_func=api.search_products, methods=["GET"])
bp.add_url_rule("/produtos/<int:product_id>", view_func=api.get_product, methods=["GET"])
bp.add_url_rule("/produtos", view_func=api.create_product, methods=["POST"])
bp.add_url_rule("/produtos/<int:product_id>", view_func=api.update_product, methods=["PUT"])
bp.add_url_rule("/produtos/<int:product_id>", view_func=api.delete_product, methods=["DELETE"])
bp.add_url_rule("/usuarios", view_func=api.list_users, methods=["GET"])
bp.add_url_rule("/usuarios/<int:user_id>", view_func=api.get_user, methods=["GET"])
bp.add_url_rule("/usuarios", view_func=api.create_user, methods=["POST"])
bp.add_url_rule("/login", view_func=api.login, methods=["POST"])
bp.add_url_rule("/pedidos", view_func=api.create_order, methods=["POST"])
bp.add_url_rule("/pedidos", view_func=api.list_orders, methods=["GET"])
bp.add_url_rule("/pedidos/usuario/<int:user_id>", view_func=lambda user_id: api.list_orders(user_id), methods=["GET"])
bp.add_url_rule("/pedidos/<int:order_id>/status", view_func=api.update_order_status, methods=["PUT"])
bp.add_url_rule("/relatorios/vendas", view_func=api.sales_report, methods=["GET"])
bp.add_url_rule("/health", view_func=api.health, methods=["GET"])

@bp.get("/")
def index():
    return jsonify({"mensagem": "Bem-vindo à API da Loja", "versao": "1.0.0", "endpoints": {"produtos": "/produtos", "usuarios": "/usuarios", "pedidos": "/pedidos", "login": "/login", "relatorios": "/relatorios/vendas", "health": "/health"}})
