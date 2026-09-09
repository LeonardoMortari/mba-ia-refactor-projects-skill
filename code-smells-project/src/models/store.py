from src.database import get_db

def public_user(row):
    return {"id": row["id"], "nome": row["nome"], "email": row["email"], "tipo": row["tipo"], "criado_em": row["criado_em"]}

def public_product(row):
    return {key: row[key] for key in ("id", "nome", "descricao", "preco", "estoque", "categoria", "ativo", "criado_em")}

def list_products():
    return [public_product(row) for row in get_db().execute("SELECT * FROM produtos ORDER BY id").fetchall()]

def find_product(product_id):
    row = get_db().execute("SELECT * FROM produtos WHERE id = ?", (product_id,)).fetchone()
    return public_product(row) if row else None

def insert_product(data):
    db = get_db(); cursor = db.execute("INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)", (data["nome"], data.get("descricao", ""), data["preco"], data["estoque"], data.get("categoria", "geral"))); db.commit(); return cursor.lastrowid

def update_product(product_id, data):
    get_db().execute("UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?", (data["nome"], data.get("descricao", ""), data["preco"], data["estoque"], data.get("categoria", "geral"), product_id)); get_db().commit()

def delete_product(product_id):
    get_db().execute("DELETE FROM produtos WHERE id = ?", (product_id,)); get_db().commit()

def list_users():
    return [public_user(row) for row in get_db().execute("SELECT * FROM usuarios ORDER BY id").fetchall()]

def find_user(user_id):
    return get_db().execute("SELECT * FROM usuarios WHERE id = ?", (user_id,)).fetchone()

def find_user_by_email(email):
    return get_db().execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()

def insert_user(name, email, password, user_type="cliente"):
    db = get_db(); cursor = db.execute("INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)", (name, email, password, user_type)); db.commit(); return cursor.lastrowid

def search_products(term="", category=None, minimum=None, maximum=None):
    clauses, values = [], []
    if term: clauses.extend(["(nome LIKE ? OR descricao LIKE ?)"]); values.extend((f"%{term}%", f"%{term}%"))
    if category: clauses.append("categoria = ?"); values.append(category)
    if minimum is not None: clauses.append("preco >= ?"); values.append(minimum)
    if maximum is not None: clauses.append("preco <= ?"); values.append(maximum)
    where = " WHERE " + " AND ".join(clauses) if clauses else ""
    return [public_product(row) for row in get_db().execute(f"SELECT * FROM produtos{where} ORDER BY id", values).fetchall()]

def list_orders(user_id=None):
    db = get_db(); where = " WHERE p.usuario_id = ?" if user_id is not None else ""; values = (user_id,) if user_id is not None else ()
    rows = db.execute(f"SELECT p.*, i.produto_id, i.quantidade, i.preco_unitario, pr.nome AS produto_nome FROM pedidos p LEFT JOIN itens_pedido i ON i.pedido_id = p.id LEFT JOIN produtos pr ON pr.id = i.produto_id{where} ORDER BY p.id, i.id", values).fetchall()
    orders = {}
    for row in rows:
        order = orders.setdefault(row["id"], {"id": row["id"], "usuario_id": row["usuario_id"], "status": row["status"], "total": row["total"], "criado_em": row["criado_em"], "itens": []})
        if row["produto_id"] is not None: order["itens"].append({"produto_id": row["produto_id"], "produto_nome": row["produto_nome"] or "Desconhecido", "quantidade": row["quantidade"], "preco_unitario": row["preco_unitario"]})
    return list(orders.values())

def create_order(user_id, items):
    db = get_db()
    try:
        total, resolved = 0, []
        for item in items:
            product = db.execute("SELECT id, nome, preco, estoque FROM produtos WHERE id = ?", (item["produto_id"],)).fetchone()
            if not product: return {"erro": f"Produto {item['produto_id']} não encontrado"}
            if product["estoque"] < item["quantidade"]: return {"erro": f"Estoque insuficiente para {product['nome']}"}
            total += product["preco"] * item["quantidade"]; resolved.append((product, item["quantidade"]))
        cursor = db.execute("INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)", (user_id, total)); order_id = cursor.lastrowid
        for product, quantity in resolved:
            db.execute("INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)", (order_id, product["id"], quantity, product["preco"]))
            db.execute("UPDATE produtos SET estoque = estoque - ? WHERE id = ?", (quantity, product["id"]))
        db.commit(); return {"pedido_id": order_id, "total": total}
    except Exception:
        db.rollback(); raise
