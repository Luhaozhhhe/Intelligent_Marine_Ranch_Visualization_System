from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # 请替换为安全的随机字符串

# ----- 登录管理配置 -----
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# 简单的用户存储示例，后续可替换为数据库
users = {
    'user': {'password': 'userpass', 'role': 'user'},
    'admin': {'password': 'adminpass', 'role': 'admin'}
}

class User(UserMixin):
    def __init__(self, username):
        self.id = username
        self.role = users[username]['role']

@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id)
    return None

# ----- 路由定义 -----
@app.route('/')
@login_required
def index():
    # 重定向到主界面
    return redirect(url_for('main'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    # 简化版登录逻辑，实际使用请添加表单验证和安全措施
    from flask import request, flash
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = users.get(username)
        if user and user['password'] == password:
            login_user(User(username))
            return redirect(url_for('index'))
        flash('用户名或密码错误')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/main')
@login_required
def main():
    return render_template('main.html')

@app.route('/underwater')
@login_required
def underwater():
    return render_template('underwater.html')

@app.route('/intelligence')
@login_required
def intelligence():
    return render_template('intelligence.html')

@app.route('/admin')
@login_required
def admin():
    # 仅管理员可访问
    if current_user.role != 'admin':
        return "权限不足", 403
    return render_template('admin.html')

if __name__ == '__main__':
    app.run(debug=True)