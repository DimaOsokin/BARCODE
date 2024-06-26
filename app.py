from flask import render_template, Flask, url_for, request, redirect

app = Flask(__name__)


menu = [{"name": "Установка", "url": "install-flask"},
        {"name": "Первое приложение", "url": "first-app"},
        {"name": "Обратная связь", "url": "contact"}]


# @app.route("/")
# def index():
#     return render_template('index.html', title="Про Flask", menu=menu)


@app.route("/about")
def about():
    return render_template('about.html', title = "О сайте", menu = menu)


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'root' and request.form['password'] == '1234':
            username = request.form['username']
            password = request.form['password']

            # Здесь можно добавить проверку введенных данных на сервере

            # Перенаправляем на другую страницу после успешной авторизации
            return redirect('/home')

    # Если не были получены данные POST-запросом,
    # показываем форму авторизации
    return render_template('login_two.html')


@app.route("/home")
def home():
    return 'Добро пожаловать на главную страницу!'


if __name__ == '__main__':
    app.run(debug=True)
