import sqlite3

def initial_sqlite(_DIR):
    DB = '{0}/data/database.sqlite3'.format(_DIR)
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
CREATE TABLE IF NOT EXISTS rpcsaved (
id INTEGER PRIMARY KEY AUTOINCREMENT,
myorder INTEGER DEFAULT 1,
name TEXT DEFAULT '',
starttime INTEGER DEFAULT 0,
endtime INTEGER DEFAULT 0,
endtimevalue INTEGER DEFAULT 180,
endtimetype INTEGER DEFAULT 0,
idclient INTEGER DEFAULT 0,
largeimage TEXT DEFAULT '',
largetext TEXT DEFAULT '',
smallimage TEXT DEFAULT '',
smalltext TEXT DEFAULT '',
description1 TEXT DEFAULT '',
description2 TEXT DEFAULT '',
button1 INTEGER DEFAULT 0,
button1name TEXT DEFAULT '',
button1url TEXT DEFAULT '',
button2 INTEGER DEFAULT 0,
button2name TEXT DEFAULT '',
button2url TEXT DEFAULT ''
);
    """)
    conn.commit()
    conn.close()

def sqlite_query(_DIR, SQL_QUERY):
    DB = '{0}/data/database.sqlite3'.format(_DIR)
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(SQL_QUERY)
    data = cur.fetchall()
    conn.close()
    return data

def db_selectoneRPC(_DIR, _ID):
    DB = '{0}/data/database.sqlite3'.format(_DIR)
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM rpcsaved WHERE id = {0}".format(_ID))
    data = cur.fetchone()
    conn.close()
    return dict(data)

def db_insertRPC(_DIR, RPC_DATA):
    DB = '{0}/data/database.sqlite3'.format(_DIR)
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO rpcsaved (name, starttime, endtime, endtimevalue, endtimetype, idclient, largeimage, largetext, smallimage, smalltext, description1, description2, button1, button1name, button1url, button2, button2name, button2url)
    VALUES (:name, :starttime, :endtime, :endtimevalue, :endtimetype, :idclient, :largeimage, :largetext, :smallimage, :smalltext, :description1, :description2, :button1, :button1name, :button1url, :button2, :button2name, :button2url)
    """, RPC_DATA)
    if cur.rowcount < 1:
        status = False
    else:
        status = True
    conn.commit()
    __data = None
    if status:
        cur.execute("SELECT last_insert_rowid() -- same as select @@identity")
        __data = cur.fetchone()
        conn.commit()

        cur.execute("UPDATE rpcsaved SET myorder = {0} WHERE id = {0}".format(__data[0]))
        conn.commit()

        cur.execute("SELECT * FROM rpcsaved WHERE id = {0}".format(__data[0]))
        data = cur.fetchone()
        if cur.rowcount < 1:
            status = False
        else:
            status = True
    conn.close()

    return data, status

def db_updateRPC(_DIR, RPC_DATA):
    DB = '{0}/data/database.sqlite3'.format(_DIR)
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""UPDATE rpcsaved SET starttime = :starttime, endtime = :endtime, endtimevalue = :endtimevalue, endtimetype = :endtimetype, idclient = :idclient, largeimage = :largeimage, largetext = :largetext, smallimage = :smallimage, smalltext = :smalltext, description1 = :description1, description2 = :description2, button1 = :button1, button1name = :button1name, button1url = :button1url, button2 = :button2, button2name = :button2name, button2url = :button2url WHERE id = :id""", RPC_DATA)
    if cur.rowcount < 1:
        status = False
    else:
        status = True
    conn.commit()
    if status:
        cur.execute("SELECT * FROM rpcsaved WHERE id = :id", RPC_DATA)
        data = cur.fetchone()
        if cur.rowcount < 1:
            status = False
        else:
            status = True
    conn.close()

    return data, status

def db_removeRPC(_DIR, RPC_DATA):
    DB = '{0}/data/database.sqlite3'.format(_DIR)
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(f"DELETE FROM rpcsaved WHERE id = :id", RPC_DATA)
    if cur.rowcount < 1:
        status = False
    else:
        status = True
    conn.commit()
    conn.close()
    return status

def updown_data(_DIR, data_dict):
    DB = '{0}/data/database.sqlite3'.format(_DIR)
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("UPDATE {0} SET myorder = :myordernew WHERE id = :idold".format(data_dict['table']), data_dict)
    if cur.rowcount < 1:
        status = False
    else:
        status = True
    conn.commit()
    cur.execute("UPDATE {0} SET myorder = :myorderold WHERE id = :idnew".format(data_dict['table']), data_dict)
    if cur.rowcount < 1:
        status = False
    else:
        status = True
    conn.commit()
    conn.close()

    return status