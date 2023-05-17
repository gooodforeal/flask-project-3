from flask import Flask, render_template, request, redirect, url_for
from werkzeug.exceptions import abort
import sqlite3


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


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
    res = max([el[0] for el in items])
    return res


def insert_to_db(con, entities):
    cursorObj = con.cursor()
    ex = 'INSERT INTO workflows(id, title, variables) VALUES(?, ?, ?)'
    cursorObj.execute(ex, entities)
    con.commit()


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


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
        mail = request.form.get("mail")
        vr = request.form.getlist("vars")
        names = item["variables"]
        for i in range(len(vr)):
            variables[names[i]] = vr[i]
        for k, v in variables.items():
            mail = mail.replace(f"{{{{{k}}}}}", v)
        mail = mail.replace("{", "")
        mail = mail.replace("}", "")
        print(variables, email, mail)
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
        if skills[0] == "": #Проверка названия на пустоту
            error = 'Задайте название'
        else:
            i = 0
            for value in skills:
                if i == 0:
                    title = value
                else:
                    res += value + ","
                i += 1
            res = res[:-1]
            number = get_number(con) + 1
            insert_to_db(con, (number, title, res))
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
