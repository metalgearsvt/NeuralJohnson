def insertChatRecord(conn, id, username, message):
    sql = '''INSERT INTO message(message_id,username,value) VALUES(?,?,?)'''
    vals = (id, username, message)
    cur = conn.cursor()
    cur.execute(sql, vals)
    conn.commit()
    cur.close()

def deleteChatRecord(conn, id):
    sql = '''DELETE FROM message WHERE message_id=?'''
    cur = conn.cursor()
    cur.execute(sql, (id,))
    conn.commit()

def deleteChatRecords(conn, username):
    sql = '''DELETE FROM message WHERE username=?'''
    cur = conn.cursor()
    cur.execute(sql, (username,))
    conn.commit()

def deleteAllChatRecords(conn):
    sql = '''DELETE FROM message WHERE 1=1'''
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()

def deleteFirstX(conn, num_to_delete):
    sql = '''DELETE FROM message 
    WHERE message_id in (
        SELECT message_id
        FROM message
        ORDER BY time ASC
        limit ?
    )'''
    cur = conn.cursor()
    cur.execute(sql, (num_to_delete,))
    conn.commit()
    return

def getMessageCount(conn):
    sql = '''SELECT COUNT(*) FROM message'''
    cur = conn.cursor()
    cur.execute(sql)
    cur_result = cur.fetchone()
    return int(cur_result[0])

def fillConfigDict(conn):
    config = {}
    sql = '''SELECT * FROM config'''
    cur = conn.cursor()
    rows = cur.execute(sql)
    for row in rows:
        config[row["key"]] = row["value"]
    return config

def getIgnoredUsers(conn):
    ignoredUsers = []
    sql = '''SELECT * FROM ignored_users'''
    cur = conn.cursor()
    rows = cur.execute(sql)
    for row in rows:
        ignoredUsers.append(row["username"])
    return ignoredUsers

def updateConf(conn, conf):
    sql = '''UPDATE config SET value = ? WHERE key = ?'''
    cur = conn.cursor()
    for k in conf:
        try:
            cur.execute(sql, (conf[k], k))
            conn.commit()
        except Exception as e:
            print(e)
