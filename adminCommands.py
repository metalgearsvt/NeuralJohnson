import util
import datalayer

def ping(args, sock, conn, conf):
    util.sendMaintenance(sock, conf["CHANNEL"], "Yeah, I'm alive and learning.")
    return True

def toggle(args, sock, conn, conf):
    if conf["SEND_MESSAGES"].lower() == "true":
        conf["SEND_MESSAGES"] = "false"
        util.sendMaintenance(sock, conf["CHANNEL"], "Messages will no longer be sent.")
    elif conf["SEND_MESSAGES"].lower() == "false":
        conf["SEND_MESSAGES"] = "true"
        util.sendMaintenance(sock, conf["CHANNEL"], "Messages will now be sent.")
    datalayer.updateConf(conn, conf)
    return True

def unique(args, sock, conn, conf):
    if conf["UNIQUE"].lower() == "true":
        conf["UNIQUE"] = "false"
        util.sendMaintenance(sock, conf["CHANNEL"], "Messages will no longer be unique.")
    elif conf["UNIQUE"].lower() == "false":
        conf["UNIQUE"] = "true"
        util.sendMaintenance(sock, conf["CHANNEL"], "Messages will now be unique.")
    datalayer.updateConf(conn, conf)
    return True

def logmax(args, sock, conn, conf):
    try:
        stringNum = args[1]
        if stringNum != None:
            num = int(stringNum)
            if num <= 0:
                raise Exception
            conf["CULL_OVER"] = stringNum
            datalayer.updateConf(conn, conf)
            util.sendMaintenance(sock, conf["CHANNEL"], "Max logfile size set to: " + stringNum + ".")
    except Exception as e:
        util.sendMaintenance(sock, conf["CHANNEL"], "Current value: " + conf["CULL_OVER"] + ". To set, use: !logmax [number of messages]")
    return True

def number(args, sock, conn, conf):
    try:
        stringNum = args[1]
        if stringNum != None:
            num = int(stringNum)
            if num <= 0:
                raise Exception
            conf["GENERATE_ON"] = stringNum
            datalayer.updateConf(conn, conf)
            util.sendMaintenance(sock, conf["CHANNEL"], "Messages will now be sent after " + stringNum + " chat messages.")
    except Exception as e:
        util.sendMaintenance(sock, conf["CHANNEL"], "Current value: " + conf["GENERATE_ON"] + ". To set, use: !number [number of messages]")
    return True

def wipe(args, sock, conn, conf):
    if len(args) > 1:
        # Wipe user.
        datalayer.deleteChatRecords(conn, args[1].replace("@", "").lower())
        util.sendMaintenance(sock, conf["CHANNEL"], "Deleted chat records for " + args[1].replace("@", ""))
    else:
        try:
            datalayer.deleteAllChatRecords(conn)
            util.sendMaintenance(sock, conf["CHANNEL"], "Deleted all chat records. I am dumb now.")
        except Exception as e:
            print(e)
    return True