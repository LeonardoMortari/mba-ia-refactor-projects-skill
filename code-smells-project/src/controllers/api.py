from flask import jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash
from src.database import get_db
from src.models import store

VALID_CATEGORIES = {"informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"}
VALID_STATUSES = {"pendente", "aprovado", "enviado", "entregue", "cancelado"}

def _product_input(data):
    if not data or not all(field in data for field in ("nome", "preco", "estoque")): return None, "Nome, preço e estoque são obrigatórios"
    if not isinstance(data["nome"], str) or not 2 <= len(data["nome"]) <= 200: return None, "Nome deve ter entre 2 e 200 caracteres"
    if data["preco"] < 0 or data["estoque"] < 0: return None, "Preço e estoque não podem ser negativos"
    if data.get("categoria", "geral") not in VALID_CATEGORIES: return None, "Categoria inválida"
    return data, None

def list_products(): return jsonify({"dados": store.list_products(), "sucesso": True})

def search_products():
    args = request.args
    try:
        result = store.search_products(args.get("q", ""), args.get("categoria"), float(args["preco_min"]) if args.get("preco_min") else None, float(args["preco_max"]) if args.get("preco_max") else None)
        return jsonify({"dados": result, "total": len(result), "sucesso": True})
    except ValueError: return jsonify({"erro": "Faixa de preço inválida"}), 400

def get_product(product_id):
    product = store.find_product(product_id)
    return (jsonify({"dados": product, "sucesso": True}), 200) if product else (jsonify({"erro": "Produto não encontrado", "sucesso": False}), 404)

def create_product():
    data, error = _product_input(request.get_json(silent=True))
    if error: return jsonify({"erro": error}), 400
    return jsonify({"dados": {"id": store.insert_product(data)}, "sucesso": True, "mensagem": "Produto criado"}), 201

def update_product(product_id):
    if not store.find_product(product_id): return jsonify({"erro": "Produto não encontrado"}), 404
    data, error = _product_input(request.get_json(silent=True))
    if error: return jsonify({"erro": error}), 400
    store.update_product(product_id, data); return jsonify({"sucesso": True, "mensagem": "Produto atualizado"})

def delete_product(product_id):
    if not store.find_product(product_id): return jsonify({"erro": "Produto não encontrado"}), 404
    store.delete_product(product_id); return jsonify({"sucesso": True, "mensagem": "Produto deletado"})

def list_users(): return jsonify({"dados": store.list_users(), "sucesso": True})

def get_user(user_id):
    row = store.find_user(user_id)
    return (jsonify({"dados": store.public_user(row), "sucesso": True}), 200) if row else (jsonify({"erro": "Usuário não encontrado"}), 404)

def create_user():
    data = request.get_json(silent=True) or {}
    if not all(data.get(field) for field in ("nome", "email", "senha")): return jsonify({"erro": "Nome, email e senha são obrigatórios"}), 400
    if store.find_user_by_email(data["email"]): return jsonify({"erro": "Email já cadastrado"}), 409
    user_id = store.insert_user(data["nome"], data["email"], generate_password_hash(data["senha"]))
    return jsonify({"dados": {"id": user_id}, "sucesso": True}), 201

def login():
    data = request.get_json(silent=True) or {}; row = store.find_user_by_email(data.get("email", ""))
    valid = row and (check_password_hash(row["senha"], data.get("senha", "")) or row["senha"] == data.get("senha", ""))
    if not valid: return jsonify({"erro": "Email ou senha inválidos", "sucesso": False}), 401
    return jsonify({"dados": store.public_user(row), "sucesso": True, "mensagem": "Login OK"})

def create_order():
    data = request.get_json(silent=True) or {}
    if not data.get("usuario_id") or not data.get("itens"): return jsonify({"erro": "Usuario ID e itens são obrigatórios"}), 400
    result = store.create_order(data["usuario_id"], data["itens"])
    if "erro" in result: return jsonify({"erro": result["erro"], "sucesso": False}), 400
    return jsonify({"dados": result, "sucesso": True, "mensagem": "Pedido criado com sucesso"}), 201

def list_orders(user_id=None): return jsonify({"dados": store.list_orders(user_id), "sucesso": True})

def update_order_status(order_id):
    data = request.get_json(silent=True) or {}
    if data.get("status") not in VALID_STATUSES: return jsonify({"erro": "Status inválido"}), 400
    db = get_db(); cursor = db.execute("UPDATE pedidos SET status = ? WHERE id = ?", (data["status"], order_id)); db.commit()
    return (jsonify({"erro": "Pedido não encontrado"}), 404) if cursor.rowcount == 0 else jsonify({"sucesso": True, "mensagem": "Status atualizado"})

def sales_report():
    db = get_db(); total = db.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]; gross = db.execute("SELECT COALESCE(SUM(total), 0) FROM pedidos").fetchone()[0]
    counts = {status: db.execute("SELECT COUNT(*) FROM pedidos WHERE status = ?", (status,)).fetchone()[0] for status in ("pendente", "aprovado", "cancelado")}; discount = gross * (0.1 if gross > 10000 else 0.05 if gross > 5000 else 0.02 if gross > 1000 else 0)
    data = {"total_pedidos": total, "faturamento_bruto": round(gross, 2), "desconto_aplicavel": round(discount, 2), "faturamento_liquido": round(gross - discount, 2), "pedidos_pendentes": counts["pendente"], "pedidos_aprovados": counts["aprovado"], "pedidos_cancelados": counts["cancelado"], "ticket_medio": round(gross / total, 2) if total else 0}
    return jsonify({"dados": data, "sucesso": True})

def health():
    get_db().execute("SELECT 1"); return jsonify({"status": "ok", "database": "connected"})
