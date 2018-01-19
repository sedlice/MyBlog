# -*- coding: UTF-8 -*-

import MySQLdb


def select(sqlparam):

    return


def insert(sqlparam):
    return


def update(sqlparam):
    return


def delete(sqlparam):
    return


def conn_helper(sql):
    conn = MySQLdb.connect(user="root", password="root", host="localhost")
    conn.select_db("test")
    curr = conn.cursor()
    sql = sql
    results = curr.execute(sql)
    conn.commit()
    curr.close()
    conn.close()
    return results
