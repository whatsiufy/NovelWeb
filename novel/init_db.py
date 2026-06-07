from app import app, db
from app.models import User, Novel, Favorite

def init_db():
    with app.app_context():
        try:
            # 创建所有表
            db.create_all()
            print("数据库表创建成功！")
            
            # 检查是否有admin用户
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(username='admin', is_admin=True)
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("管理员账号创建成功！用户名: admin, 密码: admin123")
            else:
                print("管理员账号已存在")
        except Exception as e:
            print(f"初始化出错: {e}")
            print("\n如果表结构有问题，请运行 reset_db_simple.py 来重置数据库")
            print("注意：重置会删除所有现有数据！")

if __name__ == '__main__':
    init_db()
