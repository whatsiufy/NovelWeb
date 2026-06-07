from app import app, db
from app.models import User, Novel, Favorite
from datetime import datetime, timedelta
import random
from sqlalchemy import text

def seed_data():
    with app.app_context():
        # 确保数据库字符集正确
        print("正在设置数据库字符集...")
        with db.engine.connect() as conn:
            conn.execute(text("ALTER DATABASE novels CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci"))
            conn.commit()
        
        # 先重置数据库
        print("正在重置数据库...")
        db.drop_all()
        db.create_all()
        
        # 创建用户
        print("正在创建用户...")
        users = []
        
        # 管理员
        admin = User(username='admin', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)
        
        # 普通用户
        user1 = User(username='zhangsan')
        user1.set_password('123456')
        db.session.add(user1)
        
        user2 = User(username='lisi')
        user2.set_password('123456')
        db.session.add(user2)
        
        user3 = User(username='wangwu')
        user3.set_password('123456')
        db.session.add(user3)
        
        db.session.commit()
        users = [user1, user2, user3]
        
        # 示例小说数据
        print("正在创建小说...")
        novels_data = [
            {
                'title': '斗破苍穹',
                'description': '这里是属于斗气的世界，没有花俏艳丽的魔法，有的，仅仅是繁衍到巅峰的斗气！',
                'author_name': '天蚕土豆',
                'category': '玄幻',
                'user_id': user1.id,
                'download_count': 15000,
                'view_count': 85000,
                'created_at': datetime.now() - timedelta(days=300)
            },
            {
                'title': '完美世界',
                'description': '一粒尘可填海，一根草斩落日月星辰，弹指间诸天万界灰飞烟灭。',
                'author_name': '辰东',
                'category': '玄幻',
                'user_id': user1.id,
                'download_count': 12000,
                'view_count': 72000,
                'created_at': datetime.now() - timedelta(days=250)
            },
            {
                'title': '凡人修仙传',
                'description': '凡人流开山之作，讲述一个普通山村少年的修仙之路。',
                'author_name': '忘语',
                'category': '修真',
                'user_id': user2.id,
                'download_count': 9800,
                'view_count': 65000,
                'created_at': datetime.now() - timedelta(days=280)
            },
            {
                'title': '遮天',
                'description': '冰冷与黑暗并存的宇宙深处，九具龙尸拉着一座铜棺疾驰。',
                'author_name': '辰东',
                'category': '修真',
                'user_id': user2.id,
                'download_count': 8500,
                'view_count': 52000,
                'created_at': datetime.now() - timedelta(days=200)
            },
            {
                'title': '全职高手',
                'description': '网游荣耀中被誉为教科书级别的顶尖高手叶修，被俱乐部驱逐后重新回归巅峰的故事。',
                'author_name': '蝴蝶蓝',
                'category': '游戏',
                'user_id': user3.id,
                'download_count': 18000,
                'view_count': 95000,
                'created_at': datetime.now() - timedelta(days=150)
            },
            {
                'title': '鬼吹灯',
                'description': '盗墓探险类小说的开山之作，讲述胡八一、王胖子和Shirley杨的探险故事。',
                'author_name': '天下霸唱',
                'category': '悬疑',
                'user_id': user1.id,
                'download_count': 11000,
                'view_count': 68000,
                'created_at': datetime.now() - timedelta(days=350)
            },
            {
                'title': '盗墓笔记',
                'description': '五十年前，一群长沙土夫子挖到了一件战国古墓，从此开启了一段惊心动魄的盗墓之旅。',
                'author_name': '南派三叔',
                'category': '悬疑',
                'user_id': user1.id,
                'download_count': 10500,
                'view_count': 62000,
                'created_at': datetime.now() - timedelta(days=320)
            },
            {
                'title': '三体',
                'description': '中国科幻里程碑之作，讲述地球文明与三体文明的交流与对抗。',
                'author_name': '刘慈欣',
                'category': '科幻',
                'user_id': user2.id,
                'download_count': 22000,
                'view_count': 120000,
                'created_at': datetime.now() - timedelta(days=100)
            },
            {
                'title': '微微一笑很倾城',
                'description': '校园言情小说，讲述计算机系系花贝微微和校草肖奈的爱情故事。',
                'author_name': '顾漫',
                'category': '言情',
                'user_id': user3.id,
                'download_count': 9500,
                'view_count': 58000,
                'created_at': datetime.now() - timedelta(days=180)
            },
            {
                'title': '明朝那些事儿',
                'description': '以史料为基础，以年代和具体人物为主线，用幽默风趣的语言讲述明朝三百年历史。',
                'author_name': '当年明月',
                'category': '历史',
                'user_id': user2.id,
                'download_count': 7800,
                'view_count': 45000,
                'created_at': datetime.now() - timedelta(days=400)
            },
            {
                'title': '亮剑',
                'description': '讲述革命军人李云龙在战争年代的传奇经历，展现军人的铁血精神。',
                'author_name': '都梁',
                'category': '军事',
                'user_id': user3.id,
                'download_count': 6500,
                'view_count': 38000,
                'created_at': datetime.now() - timedelta(days=380)
            },
            {
                'title': '围城',
                'description': '钱钟书先生的代表作，被誉为新儒林外史，讲述方鸿渐的爱情与婚姻。',
                'author_name': '钱钟书',
                'category': '短篇',
                'user_id': user1.id,
                'download_count': 8900,
                'view_count': 52000,
                'created_at': datetime.now() - timedelta(days=500)
            },
            {
                'title': '小王子',
                'description': '一个来自B-612星球的小王子的星际旅行故事，充满哲理与诗意。',
                'author_name': '圣埃克苏佩里',
                'category': '其他',
                'user_id': user2.id,
                'download_count': 13000,
                'view_count': 75000,
                'created_at': datetime.now() - timedelta(days=60)
            },
            {
                'title': '大主宰',
                'description': '大千世界，位面交汇，万族林立，群雄荟萃，讲述少年牧尘的成长之路。',
                'author_name': '天蚕土豆',
                'category': '玄幻',
                'user_id': user1.id,
                'download_count': 7200,
                'view_count': 41000,
                'created_at': datetime.now() - timedelta(days=120)
            },
            {
                'title': '诛仙',
                'description': '天地不仁，以万物为刍狗！一个普通青年张小凡的修仙之路。',
                'author_name': '萧鼎',
                'category': '修真',
                'user_id': user3.id,
                'download_count': 9200,
                'view_count': 55000,
                'created_at': datetime.now() - timedelta(days=220)
            }
        ]
        
        novels = []
        for novel_data in novels_data:
            novel = Novel(
                title=novel_data['title'],
                description=novel_data['description'],
                author_name=novel_data['author_name'],
                filename=f"{novel_data['title']}.txt",
                user_id=novel_data['user_id'],
                category=novel_data['category'],
                download_count=novel_data['download_count'],
                view_count=novel_data['view_count'],
                created_at=novel_data['created_at']
            )
            db.session.add(novel)
            novels.append(novel)
        
        db.session.commit()
        
        # 创建一些收藏记录
        print("正在创建收藏记录...")
        for user in users:
            # 随机收藏3-8本小说
            num_favorites = random.randint(3, 8)
            selected_novels = random.sample(novels, num_favorites)
            for novel in selected_novels:
                favorite = Favorite(user_id=user.id, novel_id=novel.id)
                db.session.add(favorite)
        
        db.session.commit()
        
        print("\n数据填充完成！")
        print(f"- 用户: 4个（1个管理员，3个普通用户）")
        print(f"- 小说: {len(novels)}本")
        print(f"- 分类覆盖: 玄幻、修真、游戏、悬疑、科幻、言情、历史、军事、短篇、其他")
        print("\n账号信息:")
        print("- admin / admin123 (管理员)")
        print("- zhangsan / 123456")
        print("- lisi / 123456")
        print("- wangwu / 123456")

if __name__ == '__main__':
    seed_data()
