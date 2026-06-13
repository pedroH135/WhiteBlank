import os
import sqlite3
from flask import Flask, render_template, request, redirect, jsonify
from werkzeug.utils import secure_filename

from banco import criar_tabelas, conectar
from usuario import Usuario
from modelos import Slide
from elementos import Texto, Imagem

app = Flask(__name__)

# Configuração para Upload de Imagens do Computador
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Estados de controle ativos no Editor
projeto_atual_id = 1
slide_atual_ordem = 1
slide_teste = Slide(slide_atual_ordem)

criar_tabelas()

# ------------------------
# FUNÇÕES AUXILIARES DE PERSISTÊNCIA (SLIDES E ELEMENTOS)
# ------------------------

def carregar_slide_do_banco(slide_id, ordem_slide):
    novo_slide = Slide(ordem_slide)
    conn = conectar()
    conn.row_factory = sqlite3.Row  
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id FROM slides WHERE projeto_id = ? AND ordem = ?", (slide_id, ordem_slide))
        slide_row = cursor.fetchone()
        
        if slide_row:
            id_interno_slide = slide_row['id']
            cursor.execute("SELECT * FROM elementos WHERE slide_id = ?", (id_interno_slide,))
            elementos_banco = cursor.fetchall()
            
            for row in elementos_banco:
                if row['tipo'] == 'texto':
                    novo_slide.criar_texto(row['conteudo'], x=row['pos_x'], y=row['pos_y'])
                elif row['tipo'] == 'imagem':
                    novo_slide.criar_imagem(row['conteudo'], x=row['pos_x'], y=row['pos_y'])
            
            # Limpa o histórico após o carregamento para não desfazer a carga do banco
            novo_slide.historico.undo_stack.clear()
            novo_slide.historico.redo_stack.clear()
    except Exception as e:
        print(f"Erro ao carregar slide do banco: {e}")
    finally:
        conn.close()
    return novo_slide

def salvar_slide_no_banco(slide):
    conn = conectar()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM slides WHERE projeto_id = ? AND ordem = ?", (projeto_atual_id, slide.ordem))
        slide_row = cursor.fetchone()
        
        if not slide_row:
            cursor.execute("INSERT INTO slides (projeto_id, ordem) VALUES (?, ?)", (projeto_atual_id, slide.ordem))
            id_interno_slide = cursor.lastrowid
        else:
            id_interno_slide = slide_row['id']
            
        cursor.execute("DELETE FROM elementos WHERE slide_id = ?", (id_interno_slide,))
        
        for el in slide.elementos:
            if isinstance(el, Texto):
                cursor.execute("""
                    INSERT INTO elementos (slide_id, tipo, conteudo, largura, altura, pos_x, pos_y)
                    VALUES (?, 'texto', ?, ?, ?, ?, ?)
                """, (id_interno_slide, el.conteudo, el.largura, el.altura, el.x, el.y))
            elif isinstance(el, Imagem):
                cursor.execute("""
                    INSERT INTO elementos (slide_id, tipo, conteudo, largura, altura, pos_x, pos_y)
                    VALUES (?, 'imagem', ?, ?, ?, ?, ?)
                """, (id_interno_slide, el.nome, el.largura, el.altura, el.x, el.y))
                
        conn.commit()
    except Exception as e:
        print(f"ERROR no salvamento automático: {e}")
    finally:
        conn.close()

def obter_elementos_json(slide):
    lista_elementos = []
    for idx, el in enumerate(slide.elementos):
        if isinstance(el, Texto):
            lista_elementos.append({
                "id": idx, "tipo": "texto", "conteudo": el.conteudo,
                "largura": el.largura, "altura": el.altura,
                "x": el.x, "y": el.y  # Enviando como x e y para o JavaScript
            })
        elif isinstance(el, Imagem):
            lista_elementos.append({
                "id": idx, "tipo": "imagem", "conteudo": el.nome,
                "largura": el.largura, "altura": el.altura,
                "x": el.x, "y": el.y
            })
    return lista_elementos

# ------------------------
# ROTAS DE AUTENTICAÇÃO E INDEX
# ------------------------

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        usuario = Usuario.login(request.form['email'], request.form['senha'])
        if usuario:
            return redirect('/index')
        else:
            return "Email ou senha incorretos"
    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        usuario = Usuario(request.form['email'], request.form['senha'])
        usuario.salvar()
        return redirect('/')
    return render_template('cadastro.html')

@app.route('/index')
def index():
    conn = conectar()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 1. Busca os projetos
    cursor.execute("SELECT * FROM projetos")
    projetos = cursor.fetchall()
    
    # 2. Busca os dados do usuário (estamos usando o ID 1 para o protótipo)
    cursor.execute("SELECT foto_perfil FROM usuarios WHERE id = 1")
    usuario = cursor.fetchone()
    conn.close()
    
    # 3. Verifica se tem foto salva, senão usa a padrão
    from flask import url_for
    caminho_foto = url_for('static', filename='default_user.png')
    
    if usuario and usuario['foto_perfil']:
        caminho_foto = usuario['foto_perfil']
        
    # 4. Envia a variável 'foto_perfil' para o HTML
    return render_template('index.html', projetos=projetos, foto_perfil=caminho_foto)

@app.route('/projeto/<int:id_projeto>')
def abrir_projeto(id_projeto):
    global projeto_atual_id, slide_atual_ordem, slide_teste
    projeto_atual_id = id_projeto
    slide_atual_ordem = 1
    slide_teste = carregar_slide_do_banco(projeto_atual_id, slide_atual_ordem)
    return render_template('projeto.html', projeto_id=id_projeto)

# ------------------------
# ROTAS DE GERENCIAMENTO DE SLIDES E ELEMENTOS
# ------------------------

@app.route('/listar_slides', methods=['GET'])
def listar_slides():
    global projeto_atual_id, slide_atual_ordem
    conn = conectar()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT ordem FROM slides WHERE projeto_id = ? ORDER BY ordem ASC", (projeto_atual_id,))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return jsonify({"slides": [1], "ativo": slide_atual_ordem})
        
    return jsonify({"slides": [r['ordem'] for r in rows], "ativo": slide_atual_ordem})

@app.route('/selecionar_slide', methods=['POST'])
def selecionar_slide():
    global slide_teste, slide_atual_ordem, projeto_atual_id
    dados = request.get_json()
    slide_atual_ordem = int(dados.get('ordem', 1))
    slide_teste = carregar_slide_do_banco(projeto_atual_id, slide_atual_ordem)
    return jsonify({"status": "ok", "elementos": obter_elementos_json(slide_teste)})

@app.route('/adicionar_slide', methods=['POST'])
def adicionar_slide():
    global projeto_atual_id, slide_teste, slide_atual_ordem
    conn = conectar()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT MAX(ordem) as ultima FROM slides WHERE projeto_id = ?", (projeto_atual_id,))
    res = cursor.fetchone()
    proxima_ordem = 1 if (res is None or res['ultima'] is None) else (res['ultima'] + 1)
    
    cursor.execute("INSERT INTO slides (projeto_id, ordem) VALUES (?, ?)", (projeto_atual_id, proxima_ordem))
    conn.commit()
    conn.close()
    
    slide_atual_ordem = proxima_ordem
    slide_teste = Slide(slide_atual_ordem)
    salvar_slide_no_banco(slide_teste)
    
    return jsonify({"status": "ok", "ativo": slide_atual_ordem})

@app.route('/criar_texto', methods=['POST'])
def criar_texto():
    global slide_teste
    slide_teste.criar_texto("Novo Texto")
    salvar_slide_no_banco(slide_teste)
    return jsonify({"status": "ok", "elementos": obter_elementos_json(slide_teste)})

@app.route('/criar_imagem', methods=['POST'])
def criar_imagem():
    global slide_teste
    arquivo = request.files.get('imagem')
    if arquivo and arquivo.filename != '':
        nome_seguro = secure_filename(arquivo.filename)
        caminho_salvar = os.path.join(app.config['UPLOAD_FOLDER'], nome_seguro)
        arquivo.save(caminho_salvar)
        
        slide_teste.criar_imagem(nome=f"/static/uploads/{nome_seguro}")
        
        # Dispara o Auto-save no banco de dados!
        salvar_slide_no_banco(slide_teste)
        return jsonify({"status": "ok", "elementos": obter_elementos_json(slide_teste)})
        
    return jsonify({"status": "erro", "mensagem": "Nenhuma imagem válida recebida."}), 400

@app.route('/atualizar_elemento', methods=['POST'])
def atualizar_elemento():
    global slide_teste
    dados = request.get_json()
    idx = dados.get('id')
    
    if idx is None or not (0 <= idx < len(slide_teste.elementos)):
        return jsonify({"status": "erro", "mensagem": "Elemento não localizado no backend"}), 400
        
    el = slide_teste.elementos[idx]
    
    # Atualiza o texto e registra no Histórico
    if 'conteudo' in dados and isinstance(el, Texto):
        if el.conteudo != dados['conteudo']:
            from command import EditarConteudoCommand
            cmd = EditarConteudoCommand(el, el.conteudo, dados['conteudo'])
            slide_teste.historico.executar(cmd)
        
    # Atualiza a posição X e Y após o arrasto e registra no Histórico
    if 'x' in dados and 'y' in dados:
        x_novo, y_novo = int(dados['x']), int(dados['y'])
        if el.x != x_novo or el.y != y_novo:
            from command import MoverElementoCommand
            cmd = MoverElementoCommand(el, el.x, el.y, x_novo, y_novo)
            slide_teste.historico.executar(cmd)
        
    # Dispara o Auto-save no banco de dados!
    salvar_slide_no_banco(slide_teste)
    return jsonify({"status": "ok"})

@app.route('/alterar_foto', methods=['POST'])
def alterar_foto():
    usuario_id = 1 # Utilizador fixo para o nosso protótipo
    arquivo = request.files.get('foto')
    
    if arquivo and arquivo.filename != '':
        nome_seguro = secure_filename(arquivo.filename)
        caminho_salvar = os.path.join(app.config['UPLOAD_FOLDER'], nome_seguro)
        arquivo.save(caminho_salvar)
        
        caminho_web = f"/static/uploads/{nome_seguro}"
        
        # Atualiza a foto na base de dados
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("UPDATE usuarios SET foto_perfil = ? WHERE id = ?", (caminho_web, usuario_id))
        conn.commit()
        conn.close()
        
        return jsonify({"status": "ok", "caminho": caminho_web})
    return jsonify({"status": "erro"}), 400

@app.route('/alterar_senha', methods=['POST'])
def alterar_senha():
    usuario_id = 1 # Utilizador fixo para o nosso protótipo
    dados = request.get_json()
    nova_senha = dados.get('nova_senha')
    
    if nova_senha:
        # Atualiza a senha na base de dados
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("UPDATE usuarios SET senha = ? WHERE id = ?", (nova_senha, usuario_id))
        conn.commit()
        conn.close()
        return jsonify({"status": "ok"})
        
    return jsonify({"status": "erro"}), 400

@app.route('/desfazer', methods=['POST'])
def desfazer():
    global slide_teste
    slide_teste.historico.desfazer()
    salvar_slide_no_banco(slide_teste)
    return jsonify({"status": "ok", "elementos": obter_elementos_json(slide_teste)})

@app.route('/refazer', methods=['POST'])
def refazer():
    global slide_teste
    slide_teste.historico.refazer()
    salvar_slide_no_banco(slide_teste)
    return jsonify({"status": "ok", "elementos": obter_elementos_json(slide_teste)})

@app.route('/excluir_slide', methods=['POST'])
def excluir_slide():
    global projeto_atual_id, slide_atual_ordem, slide_teste
    ordem_remover = int(request.get_json().get('ordem'))
    
    conn = conectar()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Encontra qual o ID interno do slide
        cursor.execute("SELECT id FROM slides WHERE projeto_id = ? AND ordem = ?", (projeto_atual_id, ordem_remover))
        row = cursor.fetchone()
        if row:
            id_interno = row['id']
            # Deleta os elementos pertencentes a ele e depois o slide
            cursor.execute("DELETE FROM elementos WHERE slide_id = ?", (id_interno,))
            cursor.execute("DELETE FROM slides WHERE id = ?", (id_interno,))
            
            # Reorganiza a ordem dos slides restantes
            cursor.execute("SELECT id FROM slides WHERE projeto_id = ? ORDER BY ordem ASC", (projeto_atual_id,))
            slides_restantes = cursor.fetchall()
            for nova_ordem, s_row in enumerate(slides_restantes, start=1):
                cursor.execute("UPDATE slides SET ordem = ? WHERE id = ?", (nova_ordem, s_row['id']))
        conn.commit()
    except Exception as e:
        print(f"Erro ao excluir slide: {e}")
    finally:
        conn.close()
        
    # Volta para o slide anterior se o atual foi deletado
    if slide_atual_ordem == ordem_remover:
        slide_atual_ordem = max(1, slide_atual_ordem - 1)
    elif slide_atual_ordem > ordem_remover:
        slide_atual_ordem -= 1
        
    # Recarrega o estado atualizado
    slide_teste = carregar_slide_do_banco(projeto_atual_id, slide_atual_ordem)
    return jsonify({"status": "ok", "ativo": slide_atual_ordem})

@app.route('/novo_projeto', methods=['POST'])
def novo_projeto():
    nome = request.form['nome']
    descricao = request.form.get('descricao', '')
    tipo = request.form.get('tipo_projeto', 'individual') # 'individual' ou 'grupo'
    dono_id = 1
    
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO projetos (nome, descricao, tipo, dono_id) 
        VALUES (?, ?, ?, ?)
    """, (nome, descricao, tipo, dono_id))
    conn.commit()
    conn.close()
    
    return redirect('/index')

if __name__ == '__main__':
    app.run(debug=True)
