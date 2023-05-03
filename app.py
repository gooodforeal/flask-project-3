import json
from flask import Flask, render_template, request
from werkzeug.exceptions import abort
import sqlite3
from datetime import datetime
import pandas as pd


app = Flask(__name__)


def get_all_positions():
    df = pd.read_excel("data.xlsx")
    return list(set(list(df["Товар"])))


def get_all_companies():
    conn = get_db_connection()
    elements = conn.execute('SELECT company FROM items').fetchall()
    res = list(set([el["company"] for el in elements]))
    return res


def get_item(item_id):
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()
    tmp = {}
    for key in item.keys():
        if key == "position":
            tmp[key] = json.loads(item[key])
        else:
            tmp[key] = item[key]
    conn.close()
    if item is None:
        abort(404)
    return tmp


def change_status(item_id):
    conn = sqlite3.connect('database.db')
    cursorObj = conn.cursor()
    ex = f'Update items set status = "выдан" where id = "{item_id}"'
    cursorObj.execute(ex)
    now = datetime.now().strftime('%d.%m.%Y, %H:%M')
    ex = f'Update items set time = "{now}" where id = "{item_id}"'
    cursorObj.execute(ex)
    conn.commit()


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/<int:item_id>', methods=['GET', 'POST'])
def item(item_id):
    if request.method == 'POST':
        if request.form.get('give_prod') == 'give_prod':
            change_status(item_id)
    elif request.method == 'GET':
        pass
    item = get_item(item_id)
    return render_template('item.html', item=item)


@app.route('/new', methods=['GET', 'POST'])
def new_item():
    if request.method == 'POST':
        if request.form.get("companies") == "":
            company = None
        else:
            company = request.form.get("companies")
        if request.form.get("date") == "":
            date = None
        else:
            date = datetime.strptime(str(request.form.get("date")), '%Y-%m-%d').strftime("%d.%m.%Y")
        new_positions = []
        c = 1
        for i in range(1, 6):
            if request.form.get(f"pos{i}") != "" and request.form.get(f"count{i}") != "":
                new_positions.append([c, request.form.get(f"pos{i}"), request.form.get(f"count{i}")])
                c += 1
        print(new_positions, company, date)
    comps = get_all_companies()
    positions = get_all_positions()
    return render_template('new_item.html', comps=comps, positions=positions)


@app.route('/')
def index():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM items').fetchall()
    conn.close()
    return render_template('index.html', items=items)


if __name__ == '__main__':
    app()
