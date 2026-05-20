from flask import Flask, render_template, request, redirect

from banco import criar_tabelas

from usuario import Usuario

app = Flask(__name__)

criar_tabelas()

# ------------------------
# ROTA LOGIN
# ------------------------

@app.route('/', methods=['GET', 'POST'])

def home():

    if request.method == 'POST':

        email = request.form['email']

        senha = request.form['senha']

        usuario = Usuario.login(email, senha)

        if usuario:

            return redirect('/index')

        else:

            return "Email ou senha incorretos"

    return render_template('login.html')

# ------------------------
# ROTA CADASTRO
# ------------------------

@app.route('/cadastro', methods=['GET', 'POST'])

def cadastro():

    if request.method == 'POST':

        email = request.form['email']

        senha = request.form['senha']

        usuario = Usuario(email, senha)

        usuario.salvar()

        return redirect('/')

    return render_template('cadastro.html')


@app.route('/index')
def index():

    from banco import conectar

    conn = conectar()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT *

        FROM projetos

    """)

    projetos = cursor.fetchall()

    conn.close()

    return render_template(
        'index.html',
        projetos=projetos
    )

@app.route('/projeto/<int:id_projeto>')
def abrir_projeto(id_projeto):

    return render_template(
        'projeto.html',
        projeto_id=id_projeto
    )

@app.route('/novo_projeto', methods=['POST'])
def novo_projeto():

    nome = request.form['nome']

    dono_id = 1

    from banco import conectar

    conn = conectar()

    cursor = conn.cursor()

    cursor.execute("""

        INSERT INTO projetos(
            nome,
            dono_id
        )

        VALUES (?, ?)

    """, (

        nome,
        dono_id

    ))

    conn.commit()

    conn.close()

    return redirect('/index')

# ------------------------

if __name__ == '__main__':

    app.run(debug=True)