from replit import db
import requests
import random
from utils import *
import calendar

def xkcd(command, chatpm, user):
    x = random.randint(1, 1000000)  # For font size tags
    lasturl = "https://xkcd.com/info.0.json"
    lastresponse = requests.get(lasturl)
    lastdata = lastresponse.json()
    lastcomicid = lastdata["num"]
    blacklist = list(db.get("blacklist", []))
    blacklist.sort()
    db["blacklist"] = blacklist
    isblacklist = False
    iscomic = False
    dontoutput = False
    topiccontent = ""  # Initialize topiccontent
    comicurl = ""  # Initialize comicurl
    xkcdlink = ""  # Initialize xkcdlink
    data = {}  # Initialize data
    theblacklist = ""  # Initialize theblacklist
    if len(command) > 1:
        if command[1].lower() == "last" or command[1].lower() == "latest":
            comicurl = lastdata["img"]
            xkcdlink = "https://xkcd.com/" + str(lastcomicid)
        elif command[1] == "blacklist":
            authpeeps = db.get("authpeeps", [])
            if len(command) > 3 and command[2].lower() == "comic":
                dontoutput = True
                if user in authpeeps:
                    if (
                        float(command[3]) > 0
                        and float(command[3]) <= lastcomicid
                        and isinteger(command[3])
                    ):
                        if int(command[3]) in blacklist:
                            topiccontent = f"**[AUTOMATED]**\nThis xkcd comic is already in the blacklist. <font size={x}>"
                        else:
                            blacklist.append(int(command[3]))
                            db["blacklist"] = blacklist
                            topiccontent = f"**[AUTOMATED]**\nXKCD Comic #{command[3]} has been successfully added to the blacklist.<font size={x}>"
                    else:
                        topiccontent = f"**[AUTOMATED]**\n{command[3]} is not a valid XKCD comic ID. This is because a comic with this ID does not exist. <font size={x}>"
                else:
                    topiccontent = f"**[AUTOMATED]**\nYou are not authorized to use this command.<font size={x}>"
            else:
                isblacklist = True
                theblacklist = ", ".join(map(str, blacklist))
                theblacklist = theblacklist + "."
        elif isnumber(command[1]):
            if (
                float(command[1]) > 0
                and float(command[1]) <= lastcomicid
                and isinteger(command[1])
                and float(command[1]) != 404
            ):
                if int(command[1]) in blacklist:
                    dontoutput = True
                    if chatpm:
                        topiccontent=f"**[AUTOMATED]**\nThis xkcd comic is in the blacklist."
                    else:
                        topiccontent = f"**[AUTOMATED]**\nThis xkcd comic is in the blacklist. \n\nXKCD comics can be blacklisted for:\n* Unsupported characters in title.\nNonexistent comic. \nInappropriate words.\n\n <font size={x}>"
                else:
                    comic = "https://xkcd.com/" + command[1] + "/info.0.json"
                    response = requests.get(comic)
                    data = response.json()
                    xkcdlink = "https://xkcd.com/" + command[1]
                    iscomic = 1
            else:
                dontoutput = True
                topiccontent = f"**[AUTOMATED]**\n{command[1]} is not a valid XKCD comic ID. This is because a comic with this ID does not exist. <font size={x}>"
        elif command[1].lower() == "comic":
            if len(command) == 2:
                dontoutput = True
                topiccontent = "**[AUTOMATED]**\nIt seems like you forgot to type in your ID for the xkcd.\n For more information, say `@bot help` or `@bot display help`.\n<font size={x}>"
            elif len(command) >= 3:
                if isnumber(command[2]):
                    if (
                        float(command[2]) > 0
                        and float(command[2]) <= lastcomicid
                        and isinteger(command[2])
                        and float(command[2]) != 404
                    ):
                        if int(command[2]) in blacklist:
                            dontoutput = True
                            if chatpm:
                                topiccontent=f"**[AUTOMATED]**\nThis xkcd comic is in the blacklist."
                            else:
                                topiccontent = f"**[AUTOMATED]**\nThis xkcd comic is in the blacklist. \n\nXKCD comics can be blacklisted for:\n* Unsupported characters in title.\nNonexistent comic. \nInappropriate words.\n\n <font size={x}>"
                        else:
                            comic = "https://xkcd.com/" + command[2] + "/info.0.json"
                            response = requests.get(comic)
                            data = response.json()
                            xkcdlink = "https://xkcd.com/" + command[2]
                            iscomic = 1
                    else:
                        dontoutput = True
                        topiccontent = f"**[AUTOMATED]**\n{command[2]} is not a valid XKCD comic ID. This is because a comic with this ID does not exist. <font size={x}>"
                else:
                    dontoutput = True
                    topiccontent = f"**[AUTOMATED]**\n{command[2]} is not a valid XKCD comic ID. This is because the ID is not a number."
        else:
            rand = random.randint(1, lastcomicid)
            while rand in blacklist:
                rand = random.randint(1, lastcomicid)
            comic = "https://xkcd.com/" + str(rand) + "/info.0.json"
            response = requests.get(comic)
            data = response.json()
            comicurl = data["img"]
            xkcdlink = "https://xkcd.com/" + str(rand)

    else:
        rand = random.randint(1, lastcomicid)
        while rand in blacklist:
            rand = random.randint(1, lastcomicid)
        comic = "https://xkcd.com/" + str(rand) + "/info.0.json"
        response = requests.get(comic)
        data = response.json()
        comicurl = data["img"]
        xkcdlink = "https://xkcd.com/" + str(rand)

    # print(data)
    # print(srce)
    # src2 = str(srce)
    # ================================================================
    if not dontoutput:
        if isblacklist:
            topiccontent = f"**[AUTOMATED]**\nCurrently, the following {len(blacklist)} XKCD comics are blacklisted:\n{theblacklist}\n\nXKCD comics can be blacklisted for:\n* Unsupported characters in title\nNonexistent comic \nInappropriate words\n\n<font size={x}>"
        elif iscomic:
            if data["transcript"] == "":
                topiccontent = f"**[AUTOMATED]**\n\n# {data['safe_title']} - XKCD {data['num']}\n### Published {calendar.month_name[int(data['month'])]} {data['day']}, {data['year']}\n[spoiler]![]({data['img']})[/spoiler]\n*Link: {xkcdlink}*\n\n##### **WARNING: SOME XKCD COMICS MAY NOT BE APPROPRIATE FOR ALL AUDIENCES. PLEASE VIEW THE ABOVE AT YOUR OWN RISK!** \n\n---\n\n**Description:**\n {data['alt']}\n\n<font size={x}>"
            else:
                data["transcript"] = dellast(data["transcript"])
                topiccontent = f"**[AUTOMATED]**\n\n# {data['safe_title']} - XKCD {data['num']}\n### Published {calendar.month_name[int(data['month'])]} {data['day']}, {data['year']}\n[spoiler]![]({data['img']})[/spoiler]\n*Link: {xkcdlink}*\n\n##### **WARNING: SOME XKCD COMICS MAY NOT BE APPROPRIATE FOR ALL AUDIENCES. PLEASE VIEW THE ABOVE AT YOUR OWN RISK!** \n\n---\n\n**Description:**\n {data['alt']}\n\n---\n\n[details=Transcript]\n```txt\n{data['transcript']}\n```\n[/details]\n\n<font size={x}>"
        else:
            if not chatpm:
                topiccontent = f"**[AUTOMATED]** \n[spoiler]![]({comicurl})[/spoiler]\n*source: {xkcdlink}*\n\n**WARNING: SOME XKCD COMICS MAY NOT BE APPROPRIATE FOR ALL AUDIENCES. PLEASE VIEW THE ABOVE AT YOUR OWN RISK!** \n<font size={x}>"
            else:
                topiccontent=f"**[AUTOMATED]** \n[spoiler]![]({comicurl})[/spoiler]\n\n*source: {xkcdlink}*\n\n**WARNING: SOME XKCD COMICS MAY NOT BE APPROPRIATE FOR ALL AUDIENCES. PLEASE VIEW THE ABOVE AT YOUR OWN RISK!**"
    return topiccontent