import pandas as pd
from datetime import datetime
import sqlite3
import json
from sqlite3 import Error


def read_data():
    data = {}
    df = pd.read_excel("data.xlsx")
    df = df.sort_values("Грузополучатель")
    for i, row in df.iterrows():
        data[row["Грузополучатель"]] = {}
        data[row["Грузополучатель"]]["Позиции"] = []
        data[row["Грузополучатель"]]["{{NUMBER}}"] = len(list(data.keys()))
    for i, row in df.iterrows():
        data[row["Грузополучатель"]]["{{TO}}"] = row["Грузополучатель"]
        data[row["Грузополучатель"]]["{{FROM}}"] = row["Грузоотправитель"]
        data[row["Грузополучатель"]]["{{DATE}}"] = datetime.today().date().strftime("%d.%m.%y")
        data[row["Грузополучатель"]]["Позиции"].append([len(data[row["Грузополучатель"]]["Позиции"]) + 1, row["Товар"], row["Ед."],  row["Кол-во"]])
        data[row["Грузополучатель"]]["CODE"] = f"AB{data[row['Грузополучатель']]['{{NUMBER}}']}_{datetime.today().date().strftime('%d.%m.%y')}"
    return data


def sql_connection():
    try:
        con = sqlite3.connect('database.db')
        return con
    except Error:
        print(Error)


def sql_table(con):
    cursorObj = con.cursor()
    ex = 'CREATE TABLE items(id integer PRIMARY KEY, title text, position text, company text, status text, time datetime)'
    cursorObj.execute(ex)
    con.commit()


def sql_insert(con, entities):
    cursorObj = con.cursor()
    ex = 'INSERT INTO items(id, title, position, company, status, time) VALUES(?, ?, ?, ?, ?, ?)'
    cursorObj.execute(ex, entities)
    con.commit()


def main():
    con = sql_connection()
    sql_table(con)
    for k, v in read_data().items():
        pos = json.dumps(v["Позиции"])
        print(json.loads(pos))
        entities = (v["{{NUMBER}}"], v["CODE"], pos, v["{{TO}}"], "не выдан", None)
        sql_insert(con, entities)


if __name__ == "__main__":
    main()