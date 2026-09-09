import sqlite3
from flask import g
from src.config.settings import Settings

SCHEMA = (
    "CREATE TABLE IF NOT EXISTS produtos (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, descricao TEXT, preco REAL, estoque INTEGER, categoria TEXT, ativo INTEGER DEFAULT 1, criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP)",
    "CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, email TEXT UNIQUE, senha TEXT, tipo TEXT DEFAULT 'cliente', criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP)",
    "CREATE TABLE IF NOT EXISTS pedidos (id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER, status TEXT DEFAULT 'pendente', total REAL, criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP)",
    "CREATE TABLE IF NOT EXISTS itens_pedido (id INTEGER PRIMARY KEY AUTOINCREMENT, pedido_id INTEGER, produto_id INTEGER, quantidade INTEGER, preco_unitario REAL)",
)

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(Settings.DATABASE_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

def init_db():
    db = get_db()
    for statement in SCHEMA:
        db.execute(statement)
    db.commit()
    if db.execute("SELECT COUNT(*) FROM produtos").fetchone()[0] == 0:
        db.executemany("INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)", [("Notebook Gamer", "Notebook potente para jogos", 5999.99, 10, "informatica"), ("Mouse Wireless", "Mouse sem fio ergonômico", 89.90, 50, "informatica"), ("Teclado Mecânico", "Teclado mecânico RGB", 299.90, 30, "informatica")])
    if db.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] == 0:
        db.executemany("INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)", [("Admin", "admin@loja.com", "admin123", "admin"), ("João Silva", "joao@email.com", "123456", "cliente")])
    db.commit()

def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()
