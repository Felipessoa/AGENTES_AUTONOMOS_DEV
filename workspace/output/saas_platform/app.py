from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Substitua por uma chave secreta forte
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Ou use outro banco de dados como PostgreSQL ou MySQL
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

db.create_all()  # Cria as tabelas no banco de dados, se não existirem

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id  # Armazena o ID do usuário na sessão
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Nome de usuário ou senha inválidos.', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove o ID do usuário da sessão
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('index'))


@app.route('/contato', methods=['GET', 'POST'])
def contato():
    if request.method == 'POST':
        # Lógica para processar o formulário de contato (ex: enviar email)
        nome = request.form['nome']
        email = request.form['email']
        mensagem = request.form['mensagem']
        # ... (código para enviar email ou armazenar a mensagem)
        flash('Mensagem enviada com sucesso!', 'success')
        return redirect(url_for('contato'))
    return render_template('contato.html')


# Outras rotas e funcionalidades podem ser adicionadas aqui

if __name__ == '__main__':
    app.run(debug=True)