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
    cur.close()

def deleteChatRecords(conn, username):
    sql = '''DELETE FROM message WHERE username=?'''
    cur = conn.cursor()
    cur.execute(sql, (username,))
    conn.commit()
    cur.close()

def deleteAllChatRecords(conn):
    sql = '''DELETE FROM message WHERE 1=1'''
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    cur.close()

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
    cur.close()
    return

def getAllChatMessages(conn):
    messageList = list()
    sql = '''SELECT value FROM message'''
    cur = conn.cursor()
    rows = cur.execute(sql)
    for row in rows:
        messageList.append(row["value"])
    cur.close()
    return messageList

def getMessageCount(conn):
    sql = '''SELECT COUNT(*) FROM message'''
    cur = conn.cursor()
    cur.execute(sql)
    cur_result = cur.fetchone()
    cur.close()
    return int(cur_result[0])

def fillConfigDict(conn):
    config = {}
    sql = '''SELECT * FROM config'''
    cur = conn.cursor()
    rows = cur.execute(sql)
    for row in rows:
        config[row["key"]] = row["value"]
    cur.close()
    return config

def getIgnoredUsers(conn):
    ignoredUsers = list()
    sql = '''SELECT * FROM ignored_users'''
    cur = conn.cursor()
    rows = cur.execute(sql)
    for row in rows:
        ignoredUsers.append(row["username"])
    cur.close()
    return ignoredUsers

def getGeneratedMessages(conn):
    messages = list()
    sql = '''SELECT * FROM generated_messages'''
    cur = conn.cursor()
    rows = cur.execute(sql)
    for row in rows:
        messages.append(row["value"])
    cur.close()
    return messages

def addGeneratedMessage(conn, text):
    sql = '''INSERT INTO generated_messages(value) VALUES(?)'''
    cur = conn.cursor()
    cur.execute(sql, (text,))
    conn.commit()
    cur.close()

def deleteGeneratedMessages(conn):
    sql = '''DELETE FROM generated_messages WHERE 1=1'''
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    cur.close()

def getBlacklistedWords(conn):
    messages = list()
    sql = '''SELECT * FROM blacklist'''
    cur = conn.cursor()
    rows = cur.execute(sql)
    for row in rows:
        messages.append(row["word"])
    cur.close()
    return messages

def deleteBlacklistedWord(conn, word):
    sql = '''DELETE FROM blacklist WHERE word = ?'''
    print("Deleting", word)
    cur = conn.cursor()
    cur.execute(sql, (word,))
    conn.commit()
    cur.close()

def addBlacklistWord(conn, word):
    sql = '''INSERT OR REPLACE INTO blacklist(word) VALUES(?)'''
    cur = conn.cursor()
    cur.execute(sql, (word,))
    conn.commit()
    cur.close()

def updateConf(conn, conf):
    sql = '''UPDATE config SET value = ? WHERE key = ?'''
    cur = conn.cursor()
    for k in conf:
        try:
            cur.execute(sql, (conf[k], k))
            conn.commit()
        except Exception as e:
            print(e)
    cur.close()

def getMods(conn):
    mods = list()
    sql = '''SELECT * FROM mods'''
    cur = conn.cursor()
    rows = cur.execute(sql)
    for row in rows:
        mods.append(row["username"])
    cur.close()
    return mods

def addMod(conn, username):
    sql = '''INSERT OR REPLACE INTO mods(username) VALUES(?)'''
    cur = conn.cursor()
    cur.execute(sql, (username,))
    conn.commit()
    cur.close()
    return

def deleteMods(conn):
    sql = '''DELETE FROM mods WHERE 1=1'''
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    cur.close()