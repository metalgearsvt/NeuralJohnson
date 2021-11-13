import sqlite3

SETTINGS = {
	"CHANNEL": "",		# lowercase string
	"GENERATE_ON": "25",		# number
	"ALLOW_MENTIONS": "True",	# true/false
	"UNIQUE": "True",			# true/false
	"SEND_MESSAGES": "True",	# true/false
	"CULL_OVER": "50",			# number
	"PREFIX": "-",				# single character
	"OWNER": ""		# Owner of the bot, lowercase.
}

con = sqlite3.connect('database.db')

cursor = con.cursor()

cursor.execute('''
DROP TABLE IF EXISTS "message"
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS "message" (
	"message_id"	TEXT,
	"username"	TEXT,
	"value"	TEXT,
	"time" timestamp DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY("message_id")
)
''')
cursor.execute('''
DROP TABLE IF EXISTS "ignored_users"
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS "ignored_users" (
	"username"	TEXT NOT NULL,
	PRIMARY KEY("username")
)
''')
cursor.execute('''
DROP TABLE IF EXISTS "config"
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS "config" (
	"key"	TEXT NOT NULL,
	"value"	TEXT,
	PRIMARY KEY("key")
)
''')
cursor.execute('''
DROP TABLE IF EXISTS "blacklist"
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS "blacklist" (
	"word"	TEXT NOT NULL,
	PRIMARY KEY("word")
);
''')

for k in SETTINGS:
	cursor.execute('''
	INSERT INTO config (key,value)
	VALUES (?,?)
	''', (k,SETTINGS[k]))

con.commit()
con.close()