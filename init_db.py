import pandas as pd
from datetime import datetime
import sqlite3
from sqlite3 import Error




def sql_connection():
    try:
        con = sqlite3.connect('database.db')
        return con
    except Error:
        print(Error)


def sql_table(con):
    cursorObj = con.cursor()
    ex = 'CREATE TABLE workflows(id integer PRIMARY KEY, title text, variables text)'
    cursorObj.execute(ex)
    con.commit()


def sql_insert(con, entities):
    cursorObj = con.cursor()
    ex = 'INSERT INTO workflows(id, title, variables) VALUES(?, ?, ?)'
    cursorObj.execute(ex, entities)
    con.commit()


def main():
    con = sql_connection()
    sql_insert(con, (1, "Тест", "Наименование,пер1,пер2"))


if __name__ == "__main__":
    main()