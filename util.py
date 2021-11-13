import re
from typing import cast
import datalayer
import adminCommands
import markovify

# -------------------------------------------------
# Markov Duties

# Generate a message from the database.
def generateMessage(conn, conf):
    chatMessages = datalayer.getAllChatMessages(conn)
    logString = buildLogString(chatMessages)
    markovString = markovFromString(logString, conf, conn)
    return markovString

# Build a string markovify can work with from DB object.
def buildLogString(chatMessages):
    logString = ""
    for msg in chatMessages:
        logString += msg + "\n"
    return logString

# Generate a markov string.
def markovFromString(inputString, conf, conn):
    text_model = markovify.NewlineText(inputString, state_size=2)
    foundUniqueMessage = False
    if getConfBool(conf, "UNIQUE"):
        generatedMessages = datalayer.getGeneratedMessages(conn)
        tries = 0
        while not foundUniqueMessage and tries < 20:
            testMessage = text_model.make_sentence(tries=1000)
            if not (testMessage in generatedMessages):
                foundUniqueMessage = True
            tries += 1
    else:
        testMessage = text_model.make_sentence(tries=1000)
    if foundUniqueMessage and testMessage != None:
        datalayer.addGeneratedMessage(conn, testMessage)
    return testMessage

# -------------------------------------------------
# Message parsing

# Remove mentions.
def removeMentions(message):
    return re.sub(r"@\S+", "", message)

# Check for blacklisted words.
def hasBlacklistedWord(conn, message):
    blacklistList = datalayer.getBlacklistedWords(conn)
    blacklist = set(blacklistList)
    for word in blacklist:
        if re.search(r"\b" + word, message, re.IGNORECASE):
            return True
    return False

# Check if logs need to be cleaned.
def cleanLogsIfNeeded(conn, conf):
    max_size = int(conf["CULL_OVER"])
    message_count = datalayer.getMessageCount(conn)
    if message_count >= max_size:
        deleteNumber = message_count - (max_size//2)
        datalayer.deleteFirstX(conn, deleteNumber)
        datalayer.deleteGeneratedMessages(conn)

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
    return (uniqueness > 50.0)

# Parse chat message into dict, return None if not a chat.
chatMessageRegex = r'(@.*):(.*)\!.*@.*\.tmi\.twitch\.tv PRIVMSG #(.*) :(.*)'
def getChatDict(resp):
    regex = re.search(chatMessageRegex, resp)
    if regex == None:
        return None
    badge, username, channel, message = regex.groups()
    return {"badge": badge, "username": username, "channel": channel, "message": message}

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

# Check if the bot is being whispered.
whisperRegex = r'(@.*):(.*)\!.*@.*\.tmi\.twitch\.tv WHISPER .* :(.*)'
def isWhisper(message):
    regex = re.search(whisperRegex, message)
    if regex == None:
        return None
    badges, user, message = regex.groups()
    return {"username": user.strip(), "message": message.strip()}

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
def isUserMod(badgeMap, username, conf):
    return bool(badgeMap["mod"] == "1" or "broadcaster" in badgeMap["badges"]) or username.lower() == conf["OWNER"]

# -------------------------------------------------
# Msc

# Check conf value and return bool.
def getConfBool(conf, value):
    if conf[value].lower() == "true":
        return True
    return False

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
def isAdminCommand(badgeMap, username, message, sock, conn, conf):
    if not isUserMod(badgeMap, username, conf):
        return False
    if message[0] != conf["PREFIX"]:
        return False
    datalayer.addMod(conn, username)
    commands = message.split()
    try: 
        commandMethod = getattr(adminCommands, commands[0][1:].lower())
        return commandMethod(commands, sock, conn, conf)
    except Exception as e:
        return False

def handleWhisper(sock, conn, conf, whisperInfo):
    mods = datalayer.getMods(conn)
    if whisperInfo["username"] in mods:
        # Check prefix.
        if whisperInfo["message"][0] != conf["PREFIX"]:
            return False
        commands = whisperInfo["message"].split()
        # Check that a channel was supplied.
        if len(commands) < 2:
            return False
        # Check last arg for correct channel.
        if commands[len(commands)-1].lower() != conf["CHANNEL"]:
            return False
        commands.pop()
        try: 
            commandMethod = getattr(adminCommands, commands[0][1:].lower())
            return commandMethod(commands, sock, conn, conf)
        except Exception as e:
            print(e)
            return False