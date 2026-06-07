from app import app, db
from app.models import User, Novel, Favorite

def reset_db():
    with app.app_context():
        # 先删除所有表
        print("正在删除旧表...")
        db.drop_all()
        
        # 再创建所有新表
        print("正在创建新表...")
        db.create_all()
        print("数据库表创建成功！")
        
        # 创建admin用户
        admin = User(username='admin', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("管理员账号创建成功！用户名: admin, 密码: admin123")
        
        print("\n数据库重置完成！")

if __name__ == '__main__':
    reset_db()
