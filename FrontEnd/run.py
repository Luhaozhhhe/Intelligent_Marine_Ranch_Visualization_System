# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# fish.csv
import pandas as pd
import numpy as np
from flask import jsonify, request
# fish.csv

import os
from   flask_migrate import Migrate
from   flask_minify  import Minify
from   sys import exit

from apps.config import config_dict, Config
from apps.authentication.models import Users
from apps import create_app, db

# WARNING: Don't run with debug turned on in production!
DEBUG = (os.getenv('DEBUG', 'False') == 'True')

# The configuration
get_config_mode = 'Debug' if DEBUG else 'Production'

try:

    # Load the configuration using the default values
    app_config = config_dict[get_config_mode.capitalize()]

except KeyError:
    exit('Error: Invalid <config_mode>. Expected values [Debug, Production] ')

app = create_app(app_config)

# fish.csv
# CSV 文件路径
FISH_CSV_PATH = os.path.join('..', 'Data', 'Fish.csv')

# 读取数据
fish_data = pd.read_csv(FISH_CSV_PATH)

@app.route('/api/fish_data', methods=['GET'])
def get_fish_data():
    species = request.args.get('species')
    parameter = request.args.get('parameter')

    # 过滤数据
    filtered_data = fish_data[fish_data['Species'] == species][parameter]

    # 计算区间
    min_val, max_val = filtered_data.min(), filtered_data.max()
    bins = np.linspace(min_val, max_val, 10)
    labels = [f'{round(bins[i], 2)} - {round(bins[i + 1], 2)}' for i in range(len(bins) - 1)]
    hist, _ = np.histogram(filtered_data, bins=bins)

    response_data = {
        "labels": labels,
        "values": hist.tolist()
    }
    return jsonify(response_data)
# fish.csv

# Create tables & Fallback to SQLite
with app.app_context():
    
    try:
        db.create_all()
    except Exception as e:

        print('> Error: DBMS Exception: ' + str(e) )

        # fallback to SQLite
        basedir = os.path.abspath(os.path.dirname(__file__))
        app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')

        print('> Fallback to SQLite ')
        db.create_all()

# Apply all changes
Migrate(app, db)

if not DEBUG:
    Minify(app=app, html=True, js=False, cssless=False)
    
if DEBUG:
    app.logger.info('DEBUG            = ' + str(DEBUG)             )
    app.logger.info('Page Compression = ' + 'FALSE' if DEBUG else 'TRUE' )
    app.logger.info('DBMS             = ' + app_config.SQLALCHEMY_DATABASE_URI)

if __name__ == "__main__":
    with app.app_context():
        # 检查管理员用户是否已存在
        adminuser = Users.query.filter_by(email=Config.ADMIN_EMAIL).first()
        
        if not adminuser:
            # 创建管理员用户（仅当用户不存在时）
            adminuser = Users(
                username='admin',
                email=Config.ADMIN_EMAIL,
                password=Config.ADMIN_PASS
            )
            db.session.add(adminuser)
            
            try:
                db.session.commit()
                print("管理员用户创建成功")
            except Exception as e:
                db.session.rollback()
                print(f"创建管理员用户失败: {str(e)}")
        else:
            print("管理员用户已存在，跳过创建")

    app.run()
