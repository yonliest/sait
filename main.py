import psycopg2
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from Models.users import User
from data.database_controller import *
from werkzeug.security import generate_password_hash, check_password_hash
from product import *
from orders import *

app = Flask(__name__)
app.secret_key = "secret_key_krytoi_sait"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"




@app.route("/")
def index():
    return render_template('index.html', a=load_products())


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cs = connection_string()
        with psycopg2.connect(host=cs["host"], user=cs["user"], password=cs["password"], dbname=cs["dbname"]) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT \"ID\", \"Login\", \"Password\" FROM \"Users\" WHERE \"Login\" = %s", (username,))
                user_data = cursor.fetchone()
                if user_data:
                    user = User(user_data[0], user_data[1], user_data[2])
                    if check_password_hash(user.password, password):
                        login_user(user)
                        print('Вы успешно вошли!', 'success')
                        return redirect(url_for('profile'))
                    else:
                        print('Неверный пароль.', 'error')
                else:
                    print('Пользователь не найден.', 'error')

    return render_template('login.html')

# Маршрут для выхода
@app.route('/logout')
@login_required
def logout():
    logout_user()
    print('Вы успешно вышли!', 'success')
    return redirect(url_for('login'))

# Маршрут для регистрации
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cs = connection_string()
        with psycopg2.connect(host=cs["host"], user=cs["user"], password=cs["password"], dbname=cs["dbname"]) as conn:
            with conn.cursor() as cursor:
                hashed_password = generate_password_hash(password)
                cursor.execute("INSERT INTO \"Users\" (\"Login\", \"Password\") VALUES (%s, %s)", (username, hashed_password))
                conn.commit()
                print('Вы успешно зарегистрировались!', 'success')
                return redirect(url_for('login'))

    return render_template('register.html')



# Загрузка пользователя по ID
@login_manager.user_loader
def load_user(user_id):
    cs = connection_string()
    with psycopg2.connect(host=cs["host"], user=cs["user"], password=cs["password"], dbname=cs["dbname"]) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT \"ID\", \"Login\", \"Password\" FROM \"Users\" WHERE \"ID\" = %s", (user_id,)) # Исправить на названия столбцов своей таблицы
            user_data = cursor.fetchone() # Получаем данные пользователя
            if user_data: # Если найден - отдаем данные
                return User(user_data[0], user_data[1], user_data[2]) # Создаем экзепляр класса пользователя
            return None

# Защищенный маршрут профиля
@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)


def load_products():
    cs = connection_string()
    with psycopg2.connect(host=cs["host"], user=cs["user"], password=cs["password"], dbname=cs["dbname"]) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM \"Products\"")
            result = cursor.fetchall()
            unpacked_products = []
            for i in result:
                unpacked_products.append(Products(i[0], i[1], i[2], i[3], i[4], i[5], i[6]))
            return unpacked_products


@app.route('/product/<id>')
def product(id):
    a = load_products()
    product = a[int(id)]
    return render_template('product.html', product=product)


def load_cart():
    cs = connection_string()
    with psycopg2.connect(host=cs["host"], user=cs["user"], password=cs["password"], dbname=cs["dbname"]) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT \"Products\".* , \"Orders\".\"quantity\" FROM \"Products\" JOIN \"Orders\" ON \"Products\".\"ID\" = \"Orders\".\"product_ID\" WHERE \"Orders\".\"user_ID\" = %s", (current_user.id,))
            result = cursor.fetchall()
            unpacked_products = []
            for i in result:
                unpacked_products.append(Products(i[0], i[1], i[2], i[3], i[4], i[5], i[6]))
            return unpacked_products

@login_required
@app.route('/cart')
def cart():
    user_id = current_user.id
    pr_oducts = load_cart()
    sum_money = 0
    for i in pr_oducts:
        sum_money += i.cost
    return render_template('cart.html', products=pr_oducts, sum_money=sum_money)


@login_required
@app.route("/add-to-cart/<product_ID>")
def add_to_cart(product_ID):
    user_id = current_user.id
    add_product_from_user(user_id, product_ID)
    return redirect(url_for("cart"))


def add_product_from_user(user_id, product_ID):
    cs = connection_string()
    with psycopg2.connect(host=cs["host"], user=cs["user"], password=cs["password"], dbname=cs["dbname"]) as conn:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO \"Orders\"(\"user_ID\", \"product_ID\", \"quantity\") VALUES (%s, %s, %s)", (current_user.id, product_ID, 1))
            conn.commit()


if __name__ == "__main__":
    app.run(debug=True, port=5002)