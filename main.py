from flask import Flask, render_template, request, send_file, redirect, url_for
from reportlab.lib import pagesizes
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
import qrcode

app = Flask(__name__)

# валидный логин и пароль для авторизации на сайте
need_passwd, need_login = '1', '1'


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Проверка корректности логина и пароля
        if username == need_passwd and password == need_login:
            return redirect(url_for('cable_production'))
        else:
            return render_template('login_password.html')

    return render_template('login_password.html')


@app.route('/cable_production', methods=['GET', 'POST'])
def cable_production():
    if request.method == 'POST':
        # значение из поля ввода
        SAP = request.form.get('input')
        # значение из выпадающего списка
        operation = request.form.get('select')

        # превращение операции в 4-х символьную строку
        if operation == 'UC':
            operation = ' UC '
        elif operation == 'MS':
            operation = ' MS '
        elif operation == 'WT':
            operation = ' WT '
        elif operation == 'Выбрать':
            operation = '____'

        # вычисление count
        count = open_file_for_count(SAP, operation)

        # формирование qrcode
        qr = qrcode.QRCode(
            version=None,
            box_size=10,
            border=4,
            error_correction=qrcode.constants.ERROR_CORRECT_L)
        qr.add_data(f"{SAP} {operation} {count}")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")

        # формирование PDF
        pdf_file_name = 'tmp/pdf.pdf'
        c = canvas.Canvas(pdf_file_name, pagesize=landscape(A4))

        # Задаем размеры элементов находящихся на странице на сайте
        PAGE_WIDTH, PAGE_HEIGHT = pagesizes.A4
        qr_code_width = 500
        qr_code_height = 500
        qr_x = (PAGE_HEIGHT - qr_code_height) / 2
        qr_y = (PAGE_WIDTH - qr_code_width) / 2

        # Сохраняем QR-код в файл
        qr_img_path = 'tmp/qr_code.png'
        qr_img.save(qr_img_path)

        # размещение QR-кода на листе
        c.drawImage(qr_img_path, qr_x + (qr_x / 3), qr_y + (qr_y / 0.75), width=qr_code_width, height=qr_code_height)

        # размещение текста на листе
        c.setFont("Helvetica-Bold", 58)
        c.drawString((PAGE_HEIGHT / 8), qr_y + (qr_y / 0.75), f"{SAP} {operation} {count}")
        c.save()

        return send_file(pdf_file_name, mimetype='application/pdf')

    return render_template('cable_production.html')


def open_file_for_count(SAP, operation) -> str:
    """
    Проверяет в корневой папке наличие file.txt с именем SAP и operation
    Если отсутствует, то создает новый со значением start_count
    Если существует, то добавляет +1 к значению

    :return count
    """

    # стартовое число для новосозданных наклеек
    start_count = '100000001'
    # число в файле, если он пустой - приобретает значение start_count
    count = ''

    # создает файл
    # если файл существует, то +считывает значение с прибавлением 1 и запись в переменную count
    with open(file=f'counts_operation/{SAP} {operation}.txt', mode='a+', encoding='utf-8') as check_file:
        # установление курсора в начало файла
        check_file.seek(0)
        data_file = check_file.read()

        # если пустой файл
        if data_file == '':
            check_file.write(start_count)
            count = start_count
        # если в файле есть данные
        else:
            try:
                count = str(int(data_file) + 1)
                check_file.write(count)
            # если в файле присутствуют не только цифры, но и другие символы
            except:
                count = data_file
                check_file.write(count)

    # перезаписать файл добавив значение из count
    with open(file=f'counts_operation/{SAP} {operation}.txt', mode='w', encoding='utf-8') as file_write:
        file_write.write(count)

    return count


if __name__ == '__main__':
    app.run(debug=True)
