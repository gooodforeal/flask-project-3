from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.exceptions import abort
import sqlite3
import os
from docx import Document
from werkzeug.utils import secure_filename
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
import email.encoders as encoders
import os
#flask --app app run --debug

UPLOAD_FOLDER = 'docs'
ALLOWED_EXTENSIONS = {'docx'}
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


#lpfyldfgrnnzdtpp
def send_mail(email):
    filepath = "result.docx"
    basename = os.path.basename(filepath)
    address = "2390603@gmail.com"

    # Compose attachment
    part = MIMEBase('application', "octet-stream")
    part.set_payload(open(filepath, "rb").read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="%s"' % basename)

    # Compose message
    msg = MIMEMultipart()
    msg['Subject'] = "Workflow project"
    msg['From'] = address
    msg['To'] = email
    msg.attach(part)

    # Send mail
    server = smtplib.SMTP('smtp.gmail.com', 25)
    server.starttls()
    server.login(address, "lpfyldfgrnnzdtpp")
    text = msg.as_string()
    server.sendmail(address, email, msg.as_string())
    server.quit()


def replace_text(paragraph, key, value):
    if key in paragraph.text:
        paragraph.text = paragraph.text.replace(key, value)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_item(item_id):
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM workflows WHERE id = ?', (item_id,)).fetchone()
    tmp = {}
    for key in item.keys():
        if key == "variables":
            tmp[key] = item[key].split(",")
        else:
            tmp[key] = item[key]
    conn.close()
    if item is None:
        abort(404)
    return tmp


def get_number(con):
    cursorObj = con.cursor()
    ex = 'SELECT id FROM workflows'
    items = cursorObj.execute(ex).fetchall()
    if len(items):
        res = max([el[0] for el in items])
    else:
        res = 1
    return res


def insert_to_db(con, entities):
    cursorObj = con.cursor()
    ex = 'INSERT INTO workflows(id, title, variables, filename) VALUES(?, ?, ?, ?)'
    cursorObj.execute(ex, entities)
    con.commit()


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_filename_by_id(ide):
    conn = sqlite3.connect('database.db')
    cursorObj = conn.cursor()
    ex = f'select filename from workflows where id = "{ide}"'
    res = cursorObj.execute(ex).fetchone()
    return res

@app.route('/<int:item_id>')
def item(item_id):
    item = get_item(item_id)
    return render_template('item.html', item=item)


@app.route('/launch/<int:item_id>', methods=["POST", "GET"])
def launch(item_id):
    item = get_item(item_id)
    if request.method == 'POST':
        variables = {}
        email = request.form.get("email")
        vr = request.form.getlist("vars")
        names = item["variables"]
        for i in range(len(vr)):
            variables[f"{{{{{names[i]}}}}}"] = vr[i]
        filename = get_filename_by_id(item_id)[0]
        tmp_doc = Document(f"docs/{filename}")
        result = "result.docx"
        for k, v in variables.items():
            for par in tmp_doc.paragraphs:
                replace_text(par, k, v)
        tmp_doc.save(result)
        send_mail(email)
        os.remove(result)
        return redirect(url_for('index'))
    return render_template('launch.html', item=item)


@app.route('/new', methods=["POST", "GET"])
def new_item():
    error = None
    con = get_db_connection()
    if request.method == 'POST':
        skills = request.form.getlist('skill[]')
        res = ""
        title = ""
        if skills[0] == "":
            error = 'Задайте название'
        else:
            i = 0
            print(skills)
            for value in skills:
                if i == 0:
                    title = value
                else:
                    res += value + ","
                i += 1
            res = res[:-1]
            number = get_number(con) + 1
            if 'file' not in request.files:
                flash('Не могу прочитать файл')
                return redirect(request.url)
            file = request.files['file']
            if file.filename == '':
                flash('Нет выбранного файла')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                insert_to_db(con, (number, title, res, filename))
            return redirect(url_for('index'))
    return render_template('new_item.html', error=error)


@app.route('/')
def index():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM workflows').fetchall()
    conn.close()
    return render_template('index.html', items=items)


if __name__ == '__main__':
    app()
