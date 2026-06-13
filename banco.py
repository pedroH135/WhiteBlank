import sqlite3

def conectar():
    conn = sqlite3.connect('database.db')

    conn.row_factory = sqlite3.Row

    return conn

def criar_tabelas():

    conn = conectar()

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        email TEXT UNIQUE NOT NULL,

        senha TEXT NOT NULL,

        biografia TEXT,

        foto_perfil TEXT,

        modo_restrito INTEGER DEFAULT 0
    )
    """)

    #Projetos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projetos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        descricao TEXT,                 -- Nova coluna de descrição
        tipo TEXT DEFAULT 'individual', -- Nova coluna para individual/grupo
        dono_id INTEGER,
        FOREIGN KEY(dono_id) REFERENCES usuarios(id)
    )
    """)


    #Slides
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS slides(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        ordem INTEGER,

        projeto_id INTEGER,

        FOREIGN KEY(projeto_id) REFERENCES projetos(id)
    )
    """)

    #elementos
    # Em banco.py, certifique-se de que a tabela de elementos possui os campos necessários:
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS elementos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slide_id INTEGER,
        tipo TEXT NOT NULL,         -- 'texto' ou 'imagem'
        conteudo TEXT,              -- Texto digitado ou o caminho da imagem
        largura INTEGER DEFAULT 200,
        altura INTEGER DEFAULT 50,
        pos_x INTEGER DEFAULT 100,  -- Adicionado para salvamento de posição
        pos_y INTEGER DEFAULT 100,  -- Adicionado para salvamento de posição
        FOREIGN KEY(slide_id) REFERENCES slides(id)
    )
    """)
    conn.commit()

    conn.close()