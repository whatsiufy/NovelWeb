from flask import render_template, redirect, url_for, request, flash, send_from_directory, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from app.models import User, Novel, Favorite
import os
from flask import current_app
from sqlalchemy import func

PER_PAGE = 9

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    
    query = Novel.query
    if search:
        query = query.filter(
            db.or_(
                Novel.title.like(f'%{search}%'),
                Novel.author_name.like(f'%{search}%')
            )
        )
    
    pagination = query.order_by(Novel.created_at.desc()).paginate(page=page, per_page=PER_PAGE, error_out=False)
    novels = pagination.items
    
    favorite_novel_ids = []
    if current_user.is_authenticated:
        favorite_novel_ids = [f.novel_id for f in current_user.favorites]
    
    return render_template('index.html', novels=novels, pagination=pagination, search=search, favorite_novel_ids=favorite_novel_ids)

@app.route('/search')
def search():
    query = request.args.get('q', '', type=str)
    page = request.args.get('page', 1, type=int)
    
    if not query:
        return redirect(url_for('index'))
    
    pagination = Novel.query.filter(
        db.or_(
            Novel.title.like(f'%{query}%'),
            Novel.author_name.like(f'%{query}%')
        )
    ).paginate(page=page, per_page=PER_PAGE, error_out=False)
    novels = pagination.items
    
    favorite_novel_ids = []
    if current_user.is_authenticated:
        favorite_novel_ids = [f.novel_id for f in current_user.favorites]
    
    return render_template('index.html', novels=novels, pagination=pagination, search=query, favorite_novel_ids=favorite_novel_ids)

@app.route('/novel/<int:novel_id>')
def novel_detail(novel_id):
    novel = Novel.query.get_or_404(novel_id)
    novel.view_count += 1
    db.session.commit()
    
    is_favorited = False
    if current_user.is_authenticated:
        is_favorited = Favorite.query.filter_by(user_id=current_user.id, novel_id=novel_id).first() is not None
    
    return render_template('novel_detail.html', novel=novel, is_favorited=is_favorited)

@app.route('/favorite/<int:novel_id>', methods=['POST'])
@login_required
def toggle_favorite(novel_id):
    novel = Novel.query.get_or_404(novel_id)
    favorite = Favorite.query.filter_by(user_id=current_user.id, novel_id=novel_id).first()
    
    if favorite:
        db.session.delete(favorite)
        flash('已取消收藏')
    else:
        favorite = Favorite(user_id=current_user.id, novel_id=novel_id)
        db.session.add(favorite)
        flash('收藏成功')
    
    db.session.commit()
    return redirect(request.referrer or url_for('index'))

@app.route('/my_favorites')
@login_required
def my_favorites():
    page = request.args.get('page', 1, type=int)
    favorite_query = Favorite.query.filter_by(user_id=current_user.id).order_by(Favorite.created_at.desc())
    pagination = favorite_query.paginate(page=page, per_page=PER_PAGE, error_out=False)
    favorites = pagination.items
    novels = [f.novel for f in favorites]
    
    favorite_novel_ids = [f.novel_id for f in current_user.favorites]
    
    return render_template('my_favorites.html', novels=novels, pagination=pagination, favorite_novel_ids=favorite_novel_ids)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        if len(password) < 6:
            flash('密码长度至少 6 位')
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            flash('用户名已存在')
            return redirect(url_for('register'))

        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('注册成功，请登录')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, deleted=False).first()

        if not user or not user.check_password(password):
            flash('用户名或密码错误，亦或账户已注销')
            return redirect(url_for('login'))

        login_user(user)
        if user.is_admin:
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        author_name = request.form['author_name']
        category = request.form['category']
        file = request.files['file']

        if file:
            filename = file.filename
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            novel = Novel(title=title, description=description, author_name=author_name,
                          filename=filename, user_id=current_user.id,
                          category=category)
            db.session.add(novel)
            db.session.commit()
            flash('小说上传成功')
            return redirect(url_for('my_novels'))
    return render_template('upload.html')

@app.route('/my_novels')
@login_required
def my_novels():
    page = request.args.get('page', 1, type=int)
    pagination = Novel.query.filter_by(user_id=current_user.id).order_by(Novel.created_at.desc()).paginate(page=page, per_page=PER_PAGE, error_out=False)
    novels = pagination.items
    
    favorite_novel_ids = []
    if current_user.is_authenticated:
        favorite_novel_ids = [f.novel_id for f in current_user.favorites]
    
    return render_template('my_novels.html', novels=novels, pagination=pagination, favorite_novel_ids=favorite_novel_ids)

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    novel = Novel.query.get_or_404(id)
    if novel.user_id != current_user.id:
        flash('无权限删除')
        return redirect(url_for('index'))
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], novel.filename))
    db.session.delete(novel)
    db.session.commit()
    flash('小说已删除')
    return redirect(url_for('my_novels'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    novel = Novel.query.get_or_404(id)
    if novel.user_id != current_user.id:
        flash('无权限修改')
        return redirect(url_for('index'))
    if request.method == 'POST':
        novel.description = request.form['description']
        novel.author_name = request.form['author_name']
        novel.category = request.form['category']
        db.session.commit()
        flash('信息已更新')
        return redirect(url_for('my_novels'))
    return render_template('edit.html', novel=novel)

@app.route('/delete_me', methods=['POST'])
@login_required
def delete_me():
    user = User.query.get(current_user.id)
    user.deleted = True
    db.session.commit()
    logout_user()
    flash('您的账户已注销，感谢曾来到贝壳书屋！')
    return redirect(url_for('index'))

@app.route('/rank')
def rank():
    sort_by = request.args.get('sort', 'download', type=str)
    
    if sort_by == 'view':
        ranked = Novel.query.filter(Novel.view_count > 0).order_by(Novel.view_count.desc()).all()
        title = '浏览量排行'
    elif sort_by == 'favorite':
        subquery = db.session.query(
            Favorite.novel_id,
            func.count(Favorite.id).label('favorite_count')
        ).group_by(Favorite.novel_id).subquery()
        
        ranked = db.session.query(Novel).join(
            subquery, Novel.id == subquery.c.novel_id
        ).order_by(subquery.c.favorite_count.desc()).all()
        title = '收藏量排行'
    elif sort_by == 'new':
        ranked = Novel.query.order_by(Novel.created_at.desc()).all()
        title = '最新发布'
    else:
        ranked = Novel.query.filter(Novel.download_count > 0).order_by(Novel.download_count.desc()).all()
        title = '下载量排行'
    
    favorite_novel_ids = []
    if current_user.is_authenticated:
        favorite_novel_ids = [f.novel_id for f in current_user.favorites]
    
    return render_template('rank.html', ranked=ranked, title=title, sort_by=sort_by, favorite_novel_ids=favorite_novel_ids)

@app.route('/category/<string:cate>')
def category_books(cate):
    page = request.args.get('page', 1, type=int)
    pagination = Novel.query.filter_by(category=cate).order_by(Novel.created_at.desc()).paginate(page=page, per_page=PER_PAGE, error_out=False)
    novels = pagination.items
    
    favorite_novel_ids = []
    if current_user.is_authenticated:
        favorite_novel_ids = [f.novel_id for f in current_user.favorites]
    
    return render_template('category.html', novels=novels, cate=cate, pagination=pagination, favorite_novel_ids=favorite_novel_ids)

@app.route('/download/<int:novel_id>')
@login_required
def download(novel_id):
    novel = Novel.query.get_or_404(novel_id)
    novel.download_count += 1
    db.session.commit()
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], novel.filename, as_attachment=True)

@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('无权访问')
        return redirect(url_for('index'))
    users = User.query.filter_by(deleted=False).all()
    novels = Novel.query.all()
    return render_template('admin.html', users=users, novels=novels)

@app.route('/admin/user/del/<int:user_id>', methods=['POST'])
@login_required
def admin_del_user(user_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    user = User.query.get_or_404(user_id)
    user.deleted = True
    db.session.commit()
    flash('用户已软删除')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/novel/del/<int:novel_id>', methods=['POST'])
@login_required
def admin_del_novel(novel_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    novel = Novel.query.get_or_404(novel_id)
    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], novel.filename))
    db.session.delete(novel)
    db.session.commit()
    flash('小说已彻底删除')
    return redirect(url_for('admin_dashboard'))