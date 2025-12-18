"""資料庫遷移管理腳本"""
from flask import Flask
from flask_migrate import Migrate, init, migrate, upgrade
from config import Config
from models import db
import sys
import os

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# 初始化 Flask-Migrate
migrate_obj = Migrate(app, db)


def run_migrations():
    """執行資料庫遷移"""
    with app.app_context():
        migrations_dir = 'migrations'

        # 檢查是否需要初始化
        if not os.path.exists(migrations_dir):
            print("初始化資料庫遷移...")
            os.system('flask --app migrate_db db init')

        # 生成遷移腳本
        print("生成遷移腳本...")
        os.system('flask --app migrate_db db migrate -m "Add gift_name column"')

        # 應用遷移
        print("應用遷移...")
        os.system('flask --app migrate_db db upgrade')

        print("✓ 資料庫遷移完成!")


if __name__ == '__main__':
    run_migrations()
