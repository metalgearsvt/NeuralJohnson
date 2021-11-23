from conf import Conf
import util
import datalayer
import socket
import traceback
import sqlite3
import markovify

conn = sqlite3.connect(Conf.database)
conn.row_factory = sqlite3.Row
confDict = datalayer.fillConfigDict(conn)
ignoredUsers = datalayer.getIgnoredUsers(conn)

# Initialize socket.
sock = socket.socket()

# Connect to the Twitch IRC chat socket.
sock.connect((Conf.server, Conf.port))

# Authenticate with the server.
channel = confDict["CHANNEL"]
sock.send(f"PASS {Conf.token}\n".encode('utf-8'))
sock.send(f"NICK {Conf.nickname}\n".encode('utf-8'))
sock.send(f"JOIN #{channel}\n".encode('utf-8'))
# We want to see when something is deleted.
sock.send(f"CAP REQ :twitch.tv/commands\n".encode('utf-8'))
# We want to see user tags.
sock.send(f"CAP REQ :twitch.tv/tags\n".encode('utf-8'))

print("Connected", Conf.nickname + ".")

message_count = 0
  # Main loop
while True:
    try:
        # Receive socket message.
        resp = sock.recv(2048).decode('utf-8')

        if len(resp) == 0:
            print("Socket dead.")
            break
        
        # Keepalive code.
        if resp.startswith('PING'):
            sock.send("PONG\n".encode('utf-8'))
        # Actual message that isn't empty.
        elif len(resp) > 0:
            try:
                chatMessageDict = util.getChatDict(resp)
                # If we have a chat message.
                if chatMessageDict != None:
                    badgeMap = util.parseBadges(chatMessageDict["badge"])
                    message = chatMessageDict["message"].strip()
                    username = chatMessageDict["username"]

                    if username.strip().lower() == Conf.nickname.lower():
                        continue

                    if util.isUserIgnored(username, ignoredUsers):
                        continue

                    if util.isAdminCommand(badgeMap, username, message, sock, conn, confDict):
                        continue

                    if not util.getConfBool(confDict, "SEND_MESSAGES"):
                        continue
                    
                    if util.hasBlacklistedWord(conn, message):
                        continue

                    if not util.listMeetsThresholdToSave(message):
                        continue
                    
                    if not util.getConfBool(confDict, "ALLOW_MENTIONS"):
                        message = util.removeMentions(message)
                    
                    datalayer.insertChatRecord(conn, badgeMap["id"], chatMessageDict["username"], message)
                    message_count += 1
                    # Generate Markov.
                    if message_count >= int(confDict["GENERATE_ON"]):
                        # Generate message.
                        markovString = util.generateMessage(conn, confDict)
                        if markovString != None and util.getConfBool(confDict, "SEND_MESSAGES"):
                            util.sendMessage(sock, channel, markovString)
                        # Check if messages exceed threshold.
                        util.cleanLogsIfNeeded(conn, confDict)
                        # Reset count.
                        message_count = 0
                
                # Check if it's a whisper.
                whisperInfo = util.isWhisper(resp)
                if whisperInfo != None:
                    util.handleWhisper(sock, conn, confDict, whisperInfo)
                    continue

                # Check for deleted messages.
                deletedMessageId = util.getDeleteAction(resp)
                if deletedMessageId != None:
                    datalayer.deleteChatRecord(conn, deletedMessageId)
                    continue
                
                # Check for user being timed out.
                timedOutUser = util.getTimeoutAction(resp)
                if timedOutUser != None:
                    datalayer.deleteChatRecords(conn, timedOutUser)
                    continue

            except Exception as e:
                print("Inner")
                traceback.print_exc()
                print(e)
    except Exception as e:
        print("Outer")
        traceback.print_exc()
        print(e)
        break