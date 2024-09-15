from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import sqlite3
import time
import calendar
from datetime import datetime

app = Flask(__name__)

app.secret_key = os.urandom(25)

# Conectar ao banco de dados
def connect_db():
    conn = sqlite3.connect('database.db')
    return conn

# Criar tabelas
def create_tables():
    conn = connect_db()
    cursor = conn.cursor()
   
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome_psi TEXT,
                        email_psi TEXT,
                        telefone_psi TEXT,
                        crp TEXT,
                        senha_psi TEXT,
                        repete_senha TEXT)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS clientes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome_completo TEXT,
                        data_nascimento TEXT,
                        cpf TEXT,
                        endereco TEXT,
                        telefone TEXT,
                        email TEXT,
                        profissao TEXT,
                        contato TEXT)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS sessoes (
                        id_sessao INTEGER PRIMARY KEY AUTOINCREMENT,
                        cliente_sessao TEXT ,
                        data TEXT,
                        hora TEXT,
                        valor REAL,
                        observacao TEXT,
                        status_sessao TEXT,
                        status_pgto TEXT)''')
                    
    conn.commit()
    conn.close()

# Gerar calendário
def generate_calendar(year, month):
    cal = calendar.Calendar(firstweekday=6)
    dias_do_mes = cal.monthdayscalendar(year, month)

    dias_da_semana = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab']
    
    calendar_html = '<table border="1"><tr>'
    
    for day in dias_da_semana:
        calendar_html += f'<th>{day}</th>'
    calendar_html += '</tr>'
    
    for week in dias_do_mes:
        calendar_html += '<tr>'
        for day in week:
            if day == 0:
                calendar_html += '<td></td>'
            else:
                date_str = f'{year}-{month:02d}-{day:02d}'
                calendar_html += f'<td><a href="#" data-date="{date_str}">{day}</a></td>'
        calendar_html += '</tr>'
    
    calendar_html += '</table>'
    return calendar_html

# Recuperar senha
@app.route('/recuperar_senha')
def recuperar_senha():
    return render_template('recuperar_senha.html')

# Login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM usuarios WHERE email_psi = ? AND senha_psi = ?', (email, senha))
        usuario = cursor.fetchone()
        conn.close()

        if usuario:
            session['nome_psi'] = usuario[1]
            session['crp'] = usuario[4]
            return redirect(url_for('menu'))
        else:
            flash('Email ou senha inválidos!', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

# Cadastro de usuário
@app.route('/cadastro_usuario', methods=['GET', 'POST'])
def cadastro_usuario():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form['telefone']
        crp = request.form['crp']
        senha = request.form['senha']
        repete_senha = request.form['repete_senha']

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO usuarios (nome_psi, email_psi, telefone_psi, crp, senha_psi, repete_senha) VALUES (?, ?, ?, ?, ?, ?)',
                       (nome, email, telefone, crp, senha, repete_senha))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    return render_template('cadastro_usuario.html')

# Menu
@app.route('/menu')
def menu():
    nome_psi = session.get('nome_psi', 'Nome não disponível')
    crp = session.get('crp', 'CRP não disponível')
    
    return render_template('menu.html', nome_psi=nome_psi, crp=crp)   
    
# Cadastro de cliente
@app.route('/cadastro_cliente', methods=['GET', 'POST'])
def cadastro_cliente():
    if request.method == 'POST':
        nome_completo = request.form['nome_completo']
        data_nascimento = request.form['data_nascimento']
        cpf = request.form['cpf']
        endereco = request.form['endereco']
        telefone = request.form['telefone']
        email = request.form['email']
        profissao = request.form['profissao']
        contato = request.form['contato']

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO clientes (nome_completo, data_nascimento, cpf, endereco, telefone, email, profissao, contato) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                       (nome_completo, data_nascimento, cpf, endereco, telefone, email, profissao, contato))
        conn.commit()
        conn.close()
        
        flash('Cliente cadastrado com sucesso!', 'success')
        return redirect(url_for('cadastro_cliente'))

    return render_template('cadastro_cliente.html')

# Lista de clientes
@app.route('/clientes')
def clientes():
    busca = request.args.get('busca', '')
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clientes WHERE nome_completo LIKE ?', ('%' + busca + '%',))
    clientes = cursor.fetchall()
    conn.close()

    return render_template('clientes.html', clientes=clientes)

# Editar cliente
@app.route('/editar_cliente/<int:id_cliente>', methods=['GET', 'POST'])
def editar_cliente(id_cliente):
    conn = connect_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        if request.form.get('action') == 'delete':
            # Excluir cliente
            cursor.execute('DELETE FROM clientes WHERE id = ?', (id_cliente,))
            conn.commit()
            conn.close()
            flash('Cliente excluído com sucesso!', 'success')
            return redirect(url_for('clientes'))

        # Editar cliente
        nome_completo = request.form['nome_completo']
        data_nascimento = request.form['data_nascimento']
        cpf = request.form['cpf']
        endereco = request.form['endereco']
        telefone = request.form['telefone']
        email = request.form['email']
        profissao = request.form['profissao']
        contato = request.form['contato']
        
        cursor.execute('UPDATE clientes SET nome_completo=?, data_nascimento=?, cpf=?, endereco=?, telefone=?, email=?, profissao=?, contato=? WHERE id=?',
                       (nome_completo, data_nascimento, cpf, endereco, telefone, email, profissao, contato, id_cliente))
        conn.commit()
        conn.close()
        flash('Cliente atualizado com sucesso!', 'success')
        return redirect(url_for('clientes'))

    cursor.execute('SELECT * FROM clientes WHERE id = ?', (id_cliente,))
    cliente = cursor.fetchone()
    conn.close()

    return render_template('editar_cliente.html', cliente=cliente)

# Agendar sessão
@app.route('/agendar', methods=['GET', 'POST'])
def agendar():
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, nome_completo FROM clientes')
    clientes = cursor.fetchall()

    if request.method == 'POST':
        cliente_nome = request.form['cliente_sessao']
        data = request.form['data_sessao']
        hora = request.form['hora_sessao']
        valor = request.form['valor']
        observacao = request.form['observacao']
        status_sessao = "Agendada"
        status_pgto = "Em aberto"

        cursor.execute('INSERT INTO sessoes (cliente_sessao, data, hora, valor, observacao, status_sessao, status_pgto) VALUES (?, ?, ?, ?, ?, ?, ?)',
                       (cliente_nome, data, hora, valor, observacao, status_sessao, status_pgto))
        conn.commit()
        conn.close()
        
        flash('Sessão agendada com sucesso!', 'success')     
        return redirect(url_for('agendar'))

    cursor.execute('SELECT nome_completo FROM clientes')
    clientes = cursor.fetchall()
    conn.close()
    
    return render_template('agendar.html', clientes=clientes)

# Agenda
@app.route('/agenda', methods=['GET'])
def agenda():
    data_filtro = request.args.get('data', '')
    year = int(request.args.get('year', datetime.now().year))
    month = int(request.args.get('month', datetime.now().month))

    cal = generate_calendar(year, month)
    
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM sessoes WHERE data = ?', (data_filtro,))
    sessoes = cursor.fetchall()

    conn.close()

    return render_template('agenda.html', sessoes=sessoes, calendar=cal, year=year, month=month)
    
# Editar sessão
@app.route('/editar_sessao/<int:id_sessao>', methods=['GET', 'POST'])
def editar_sessao(id_sessao):
    conn = connect_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        if request.form.get('action') == 'delete':
            # Excluir sessão
            cursor.execute('DELETE FROM sessoes WHERE id_sessao = ?', (id_sessao,))
            conn.commit()
            conn.close()
            flash('Sessão excluída com sucesso!', 'success')
            return redirect(url_for('agenda'))
        
        # Atualizar sessão
        cliente_nome = request.form['cliente_sessao']
        data = request.form['data_sessao']
        hora = request.form['hora_sessao']
        valor = request.form['valor']
        observacao = request.form['observacao']
        status_sessao = request.form['status_sessao']
        status_pgto = request.form['status_pgto']
        
        cursor.execute('UPDATE sessoes SET cliente_sessao=?, data=?, hora=?, valor=?, observacao=?, status_sessao=?, status_pgto=? WHERE id_sessao=?',
                       (cliente_nome, data, hora, valor, observacao, status_sessao, status_pgto, id_sessao))
        conn.commit()
        conn.close()
        flash('Sessão atualizada com sucesso!', 'success')
        return redirect(url_for('agenda'))
    
    # Carregar dados da sessão
    cursor.execute('SELECT * FROM sessoes WHERE id_sessao = ?', (id_sessao,))
    sessao = cursor.fetchone()

    # Buscar todos os clientes
    cursor.execute('SELECT nome_completo FROM clientes')
    clientes = cursor.fetchall()
    conn.close()
    
    return render_template('editar_sessao.html', sessao=sessao, clientes=clientes)

# Relatórios
def get_report_data(start_date, end_date):
    conn = connect_db()
    cursor = conn.cursor()
    
    query = """
        SELECT
        SUM(CASE WHEN status_sessao = 'Agendada' THEN 1 ELSE 0 END) AS agendadas,
        SUM(CASE WHEN status_sessao = 'Realizada' THEN 1 ELSE 0 END) AS realizadas,
        SUM(CASE WHEN status_sessao = 'Desmarcada' THEN 1 ELSE 0 END) AS desmarcadas,
        SUM(CASE WHEN status_sessao = 'Falta' THEN 1 ELSE 0 END) AS faltas,
        SUM(CASE WHEN status_pgto = 'Pago' THEN valor ELSE 0 END) AS recebidos,
        SUM(CASE WHEN status_pgto = 'Pendente' THEN valor ELSE 0 END) AS a_receber
        FROM sessoes
        WHERE data BETWEEN ? AND ?
    """
    cursor.execute(query, (start_date, end_date))
    data = cursor.fetchone()
    conn.close()

    return tuple(0 if d is None else d for d in data)
    
@app.route('/relatorios', methods=['GET'])
def relatorios():
    data_inicial = request.args.get('data-inicial', '')
    data_final = request.args.get('data-final', '')
    
    if data_inicial and data_final:
        report_data = get_report_data(data_inicial, data_final)
        try:
            data_inicial_formatada = datetime.strptime(data_inicial, '%Y-%m-%d').strftime('%d/%m/%Y')
            data_final_formatada = datetime.strptime(data_final, '%Y-%m-%d').strftime('%d/%m/%Y')
        except ValueError:
            data_inicial_formatada = ''
            data_final_formatada = ''
    else:
        report_data = (0, 0, 0, 0, 0, 0)
        data_inicial_formatada = ''
        data_final_formatada = ''
    
    return render_template('relatorios.html', report_data=report_data, start_date=data_inicial_formatada, end_date=data_final_formatada)

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)