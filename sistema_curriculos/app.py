from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
import secrets
import sqlite3
import os



from flask_wtf import FlaskForm
from wtforms import HiddenField
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError
from flask_wtf.csrf import CSRFError

# Importando o formulário de cadastro
from forms import Cadastro_curriculoForm,BuscaForm

csrf = CSRFProtect()
app = Flask(__name__)

csrf.init_app(app) 
app.config['SESSION_TYPE'] = 'filesystem'  # Sessão baseada em arquivo
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['WTF_CSRF_TIME_LIMIT'] = None  # Desativa expiração do token para testes
app.config['WTF_CSRF_ENABLED'] = True


DATABASE = 'curriculos.db'

# Função para conectar ao banco de dados
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Para acessar as colunas como dicionários
    return conn

def criar_tabela():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS curriculos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT NOT NULL,
        telefone TEXT,
        endereco_web TEXT,
        experiencia_profissional TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

# Chame a função para criar a tabela quando o aplicativo for iniciado
criar_tabela()


# Rota para a página inicial
@app.route('/')
def index():
    return render_template('index.html')

# Rota para exibir todos os currículos
# Rota para exibir todos os currículos
@app.route('/curriculos')
def listar_curriculos():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM curriculos')
    curriculos = cursor.fetchall()
    conn.close()
    # Passando um form vazio apenas para o CSRF
    form = FlaskForm()  # Adicionando um formulário vazio apenas para o CSRF
    return render_template('listar_curriculos.html', curriculos=curriculos, form=form)


# Rota para cadastrar currículo
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    form = Cadastro_curriculoForm()
    if form.validate_on_submit():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO curriculos (nome, email, telefone, endereco_web, experiencia_profissional)
            VALUES (?, ?, ?, ?, ?)
        ''', (form.nome.data, form.email.data, form.telefone.data, form.endereco_web.data, form.experiencia_profissional.data))
        conn.commit()
        conn.close()
        return redirect(url_for('listar_curriculos'))
    return render_template('cadastro_curriculo.html', form=form)

# Rota para editar currículo
@app.route('/editar/<int:curriculo_id>', methods=['GET', 'POST'])
def editar_curriculo(curriculo_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM curriculos WHERE id = ?', (curriculo_id,))
    curriculo = cursor.fetchone()

    if not curriculo:
        abort(404, 'Currículo não encontrado.')

    form = Cadastro_curriculoForm(data=dict(curriculo))  # Preenche o formulário com os dados existentes
    if form.validate_on_submit():
        cursor.execute('''
            UPDATE curriculos
            SET nome = ?, email = ?, telefone = ?, endereco_web = ?, experiencia_profissional = ?
            WHERE id = ?
        ''', (
            form.nome.data, form.email.data, form.telefone.data,
            form.endereco_web.data, form.experiencia_profissional.data, curriculo_id
        ))
        conn.commit()
        conn.close()
        flash('Currículo atualizado com sucesso!', 'success')
        return redirect(url_for('listar_curriculos'))

    conn.close()
    return render_template('editar_curriculo.html', form=form)



# Rota para exibir detalhes do currículo

class CSRFForm(FlaskForm):
    csrf_token = HiddenField()

@app.route('/curriculo/<int:curriculo_id>')
def detalhes_curriculo(curriculo_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM curriculos WHERE id = ?', (curriculo_id,))
    curriculo = cursor.fetchone()
    conn.close()
    
    form = CSRFForm()  # Criação do formulário CSRF
    return render_template('detalhes_curriculo.html', curriculo=curriculo, form=form)


# Rota para excluir currículo
from flask import jsonify

@app.route('/excluir/<int:curriculo_id>', methods=['POST'])
def excluir_curriculo(curriculo_id):
    print("CSRF Token recebido:", request.form.get('csrf_token'))  # Log do token
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM curriculos WHERE id = ?', (curriculo_id,))
    conn.commit()
    conn.close()
    flash('Currículo excluído com sucesso!', 'success')
    return redirect(url_for('listar_curriculos'))

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return f"Erro CSRF: {e.description}", 400

@app.route('/buscar_curriculos', methods=['GET', 'POST'])
def buscar_curriculos():
    form = BuscaForm()
    if form.validate_on_submit():
        termo = form.termo_busca.data
        # Lógica para buscar currículos
        return redirect(url_for('resultado_busca', termo=termo))
    return render_template('buscar_curriculos.html', form=form)

@app.route('/resultado_busca/<termo>')
def resultado_busca(termo):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM curriculos WHERE nome LIKE ?', (f'%{termo}%',))
    resultados = cursor.fetchall()
    conn.close()
    return render_template('resultado_busca.html', resultados=resultados, termo=termo)


# Função principal para rodar o app
if __name__ == '__main__':
    app.run(debug=True)