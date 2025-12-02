from flask import render_template, redirect, url_for, request, flash, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from app.models import User, Novel
import os
from flask import send_from_directory
from flask_login import login_required
from flask import current_app   # 已经有的其他导入保持不变

@app.route('/download/<int:novel_id>')
@login_required
def download(novel_id):
    novel = Novel.query.get_or_404(novel_id)
    # 计数+1
    novel.download_count += 1
    db.session.commit()

    return send_from_directory(current_app.config['UPLOAD_FOLDER'], novel.filename, as_attachment=True)
@app.route('/')
def index():
    novels = Novel.query.all()
    return render_template('index.html', novels=novels)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        # ① 长度校验
        if len(password) < 6:
            flash('密码长度至少 6 位')
            return redirect(url_for('register'))

        # ② 重名校验
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
        # 管理员直接去后台
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
        category = request.form['category']          # ← 取分类
        file = request.files['file']

        if file:
            filename = file.filename
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            novel = Novel(title=title, description=description, author_name=author_name,
                          filename=filename, user_id=current_user.id,
                          category=category)         # ← 存分类
            db.session.add(novel)
            db.session.commit()
            flash('小说上传成功')
            return redirect(url_for('my_novels'))
    return render_template('upload.html')
@app.route('/my_novels')
@login_required
def my_novels():
    novels = Novel.query.filter_by(user_id=current_user.id).all()
    return render_template('my_novels.html', novels=novels)

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
        db.session.commit()
        flash('信息已更新')
        return redirect(url_for('my_novels'))
    return render_template('edit.html', novel=novel)

@app.route('/delete_me', methods=['POST'])
@login_required
def delete_me():
    user = User.query.get(current_user.id)
    user.deleted = True          # 软删除
    db.session.commit()
    logout_user()
    flash('您的账户已注销，感谢曾来到贝壳书屋！')
    return redirect(url_for('index'))

@app.route('/rank')
def rank():
    ranked = Novel.query.filter(Novel.download_count > 0)\
                        .order_by(Novel.download_count.desc())\
                        .all()
    return render_template('rank.html', ranked=ranked)

@app.route('/category/<string:cate>')
def category_books(cate):
    # 过滤分类 + 下载次数≥0 即可（排行另页）
    novels = Novel.query.filter_by(category=cate).all()
    return render_template('category.html', novels=novels, cate=cate)

@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('无权访问')
        return redirect(url_for('index'))
    users = User.query.filter_by(deleted=False).all()
    novels = Novel.query.all()
    return render_template('admin.html', users=users, novels=novels)

# 删除用户（软删除）
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

# 删除小说（物理删文件+库记录）
@app.route('/admin/novel/del/<int:novel_id>', methods=['POST'])
@login_required
def admin_del_novel(novel_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    novel = Novel.query.get_or_404(novel_id)
    # 删文件
    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], novel.filename))
    db.session.delete(novel)
    db.session.commit()
    flash('小说已彻底删除')
    return redirect(url_for('admin_dashboard'))