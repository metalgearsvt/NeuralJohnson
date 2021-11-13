import sqlite3
# ############################
# CONFIG HERE
# ############################
SETTINGS = {
	"CHANNEL": "",		# lowercase string
	"GENERATE_ON": "25",		# number
	"ALLOW_MENTIONS": "True",	# true/false
	"UNIQUE": "True",			# true/false
	"SEND_MESSAGES": "True",	# true/false
	"CULL_OVER": "1500",		# number
	"PREFIX": "-",				# single character
	"OWNER": ""		# Owner of the bot, lowercase.
}

IGNORED_USERS = [
	"moobot", "streamlabs", "nightbot", "fossabot", "streamelements"
]

BLACKLISTED_WORDS = [
	
]

# ############################
# END CONFIG
# ############################
 
con = sqlite3.connect('database.db')

cursor = con.cursor()

# Message table
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

# Ignored users table.
cursor.execute('''
DROP TABLE IF EXISTS "ignored_users"
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS "ignored_users" (
	"username"	TEXT NOT NULL,
	PRIMARY KEY("username")
)
''')

# Config table.
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

# Blacklist table.
cursor.execute('''
DROP TABLE IF EXISTS "blacklist"
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS "blacklist" (
	"word"	TEXT NOT NULL,
	PRIMARY KEY("word")
);
''')

# Generated messages table.
cursor.execute('''
DROP TABLE IF EXISTS "generated_messages"
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS "generated_messages" (
	"value"	TEXT NOT NULL,
	PRIMARY KEY("value")
);
''')

# Known mods.
cursor.execute('''
DROP TABLE IF EXISTS "mods"
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS "mods" (
	"username"	TEXT NOT NULL,
	PRIMARY KEY("username")
);
''')

# Set initial data.
for k in SETTINGS:
	cursor.execute('''
	INSERT OR REPLACE INTO config (key,value)
	VALUES (?,?)
	''', (k,SETTINGS[k]))

for k in IGNORED_USERS:
	cursor.execute('''
	INSERT OR REPLACE INTO ignored_users (username)
	VALUES (?)
	''', (k,))

for k in BLACKLISTED_WORDS:
	cursor.execute('''
	INSERT OR REPLACE INTO blacklist (word)
	VALUES (?)
	''', (k,))

cursor.execute('''
INSERT OR REPLACE INTO mods (username) VALUES (?)
''', (SETTINGS["CHANNEL"],))

cursor.execute('''
INSERT OR REPLACE INTO mods (username) VALUES (?)
''', (SETTINGS["OWNER"],))

con.commit()
con.close()