import re
from typing import cast
import datalayer
import adminCommands
import markovify

# TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO 
# -------------------------------------------------
# Markov Duties

# Generate a message from the database.
def generateMessage(conn, conf):
    chatMessages = datalayer.getAllChatMessages(conn)
    logString = buildLogString(chatMessages)
    markovString = markovFromString(logString)
    return

# Build a string markovify can work with from DB object.
def buildLogString(chatMessages):
    return

# Generate a markov string.
def markovFromString(inputString):
    text_model = markovify.NewlineText(inputString, state_size=2)
    return

# TODO: Add the generated messages table to prevent duplicates.
# TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO 
# -------------------------------------------------
# Message parsing

# Check if logs need to be cleaned.
def cleanLogsIfNeeded(conn, conf):
    max_size = int(conf["CULL_OVER"])
    if datalayer.getMessageCount(conn) >= max_size:
        datalayer.deleteFirstX(conn, max_size//2)

# Check if the message is mostly spam.
def listMeetsThresholdToSave(message):
    # Remove just repeated messages.
    whole = message.split()
    # Make list unique
    part = list(set(whole))
    # Math
    pF = float(len(part))
    wF = float(len(whole))
    if wF == 0:
        return False
    uniqueness = (pF/wF) * float(100)
    return (uniqueness >= 50.0)

# Parse chat message into dict, return None if not a chat.
chatMessageRegex = r'(@.*):(.*)\!.*@.*\.tmi\.twitch\.tv PRIVMSG #(.*) :(.*)'
def getChatDict(resp):
    regex = re.search(chatMessageRegex, resp)
    if regex == None:
        return None
    badge, username, channel, message = regex.groups()
    chatDict = {"badge": badge, "username": username, "channel": channel, "message": message}
    return chatDict

# Parse message deletion.
deleteMessageRegex = r'@.*target-msg-id=(.*);.*:tmi\.twitch\.tv CLEARMSG #(.*) :(.*)'
def getDeleteAction(resp):
    regex = re.search(deleteMessageRegex, resp)
    if regex == None:
        return None
    deletedMessage, channel, message = regex.groups()
    return deletedMessage

# Parse user timeout.
userTimeoutRegex = r'@.*target-user-id=(.*);.*:tmi\.twitch\.tv CLEARCHAT #(.*) :(.*)'
def getTimeoutAction(resp):
    regex = re.search(userTimeoutRegex, resp)
    if regex == None:
        return None
    userId, channel, username = regex.groups()
    return username.strip()

# -------------------------------------------------
# User badge parsing.

# Parse badges into a map from a string.
def parseBadges(badgeString):
    finalMap = {}
    badgeList = badgeString[1:].split(";")
    for a in badgeList:
        badgeMap = a.split("=")
        finalMap[badgeMap[0]] = badgeMap[1]
    return finalMap

# Return true if the user is a mod or broadcaster.
def isUserMod(badgeMap):
    return bool(badgeMap["mod"] == "1" or "broadcaster" in badgeMap["badges"])

# -------------------------------------------------
# Msc

# Check if a username is ignored.
def isUserIgnored(user, ignoredUsers):
    return user.strip() in ignoredUsers

# Send a message in the chat.
def sendMessage(sock, channel, message):
    sock.send("PRIVMSG #{} :{}\r\n".format(channel, message).encode("utf-8"))

def sendMaintenance(sock, channel, message):
    sock.send("PRIVMSG #{} :{}\r\n".format(channel, "Maintenance Message: " + message).encode("utf-8"))

# -------------------------------------------------
# Admin messages. Returns true if an admin message was handled.
def isAdminCommand(badgeMap, message, sock, conn, conf):
    if not isUserMod(badgeMap):
        return False
    if message[0] != conf["PREFIX"]:
        return False
    commands = message.split()
    try: 
        commandMethod = getattr(adminCommands, commands[0][1:])
        return commandMethod(commands, sock, conn, conf)
    except Exception as e:
        return False