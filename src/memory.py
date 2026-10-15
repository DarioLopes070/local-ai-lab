import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = Path("data") / "conversations.db"


def inicializar_banco(db_path=DEFAULT_DB_PATH):
    """Cria o banco SQLite e a tabela de mensagens, se necessário."""

    db_path = Path(db_path)

    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as conexao:
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """)


def salvar_mensagem(role, content, db_path=DEFAULT_DB_PATH):
    """Salva uma mensagem no banco de dados SQLite."""

    if role not in ("user", "assistant"):
        raise ValueError("O papel deve ser 'user' ou 'assistant'.")

    with sqlite3.connect(db_path) as conexao:
        conexao.execute(
            """
            INSERT INTO messages (role, content)
            VALUES (?, ?)
            """,
            (role, content),
        )


def carregar_mensagens(db_path=DEFAULT_DB_PATH):
    """Recupera as mensagens armazenadas no banco SQLite."""

    with sqlite3.connect(db_path) as conexao:
        registros = conexao.execute("""
            SELECT role, content
            FROM messages
            ORDER BY id ASC
            """).fetchall()

    return [{"role": role, "content": content} for role, content in registros]
