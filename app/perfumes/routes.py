from flask import render_template, request, redirect, url_for, flash
from app.perfumes import bp
from app.models import Perfume
from app import db
from app.services.log_service import LogService
from flask_login import current_user

@bp.route('/')
def index():
    perfumes = Perfume.query.order_by(Perfume.nome).all()
    return render_template('perfumes/index.html', perfumes=perfumes)

@bp.route('/add', methods=['POST'])
def add():
    nome = request.form.get('nome')
    marca = request.form.get('marca')
    correspondente = request.form.get('correspondente')
    valor = request.form.get('valor')
    url = request.form.get('url')
    url_imagem = request.form.get('url_imagem')
    
    if not nome:
        flash('O nome do perfume é obrigatório.', 'danger')
        return redirect(url_for('perfumes.index'))
    
    try:
        v_float = float(valor) if valor else None
    except ValueError:
        v_float = None
        
    novo_perfume = Perfume(
        nome=nome,
        marca=marca,
        correspondente=correspondente,
        valor=v_float,
        url=url,
        url_imagem=url_imagem
    )
    db.session.add(novo_perfume)
    db.session.commit()
    LogService.log_action(current_user, 'PERFUME_CREATED', f'ID: {novo_perfume.id} | NOME: {nome}')
    flash('Perfume cadastrado com sucesso!', 'success')
    return redirect(url_for('perfumes.index'))

@bp.route('/edit/<int:id>', methods=['POST'])
def edit(id):
    perfume = Perfume.query.get_or_404(id)
    nome = request.form.get('nome')
    marca = request.form.get('marca')
    correspondente = request.form.get('correspondente')
    valor = request.form.get('valor')
    url = request.form.get('url')
    url_imagem = request.form.get('url_imagem')
    
    if not nome:
        flash('O nome do perfume é obrigatório.', 'danger')
        return redirect(url_for('perfumes.index'))
        
    try:
        v_float = float(valor) if valor else None
    except ValueError:
        v_float = None

    perfume.nome = nome
    perfume.marca = marca
    perfume.correspondente = correspondente
    perfume.valor = v_float
    perfume.url = url
    perfume.url_imagem = url_imagem
    
    db.session.commit()
    LogService.log_action(current_user, 'PERFUME_EDITED', f'ID: {id} | NOVO_NOME: {nome}')
    flash('Perfume atualizado com sucesso!', 'success')
    return redirect(url_for('perfumes.index'))

@bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    perfume = Perfume.query.get_or_404(id)
    nome = perfume.nome
    db.session.delete(perfume)
    db.session.commit()
    LogService.log_action(current_user, 'PERFUME_DELETED', f'ID: {id} | NOME: {nome}')
    flash('Perfume removido com sucesso!', 'success')
    return redirect(url_for('perfumes.index'))
