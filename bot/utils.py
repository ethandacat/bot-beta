import re, random, datetime, time, requests
from replit import db

def getpost(link):
    match = re.search(r'(\d+)$', link)
    slash = link.count("/")
    #print("slash",slash)
    if (slash == 5):
        return 1
    if match:
        return int(match.group(1))
    else:
        return None


def clean(text):
    non_bmp_pattern = re.compile(r'[\U00010000-\U0010FFFF]', flags=re.UNICODE)
    return non_bmp_pattern.sub('', text)


def checkbmp(s):
    if any(ord(char) > 0xFFFF for char in s):
        return "Sorry for the inconvenience, but the `say` command only supports BMP characters."
    return s


def dellast(text):
    lines = text.split("\n")
    return "\n".join(lines[:-2]) if len(lines) > 1 else ""


def isnumber(s):
    try:
        float(s)
    except ValueError:
        return False
    else:
        return True


def isinteger(s):
    try:
        int(s)
    except ValueError:
        return False
    else:
        return True
        
def suffix(d):
    return "th" if 11 <= d <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(d % 10, "th")
def diceroll(t, d):
    output="**[AUTOMATED]**\n"
    if t==0:
        output+=f"\nYou rolled nothing."
        return output
    if t<0 or d<1:
        output+=f"\nI’m sorry, it is mathematically impossible to roll that combination of dice. :confounded:"
        return output
    ot=1
    if t>20:
        t=20
        output+="I only have 20 dice. Shameful, I know!\n"
        ot=0
    if d>120:
        d=120
        if ot==0:
            output+="\n"
        output+="Did you know that [the maximum number of sides](https://www.wired.com/2016/05/mathematical-challenge-of-designing-the-worlds-most-complex-120-sided-dice/) for a mathematically fair dice is 120?\n"
    output+="> :game_die: "    
    for i in range(t):
        if (i==t-1):
            output+=str(random.randint(1,d))
        else:
            output+=str(random.randint(1,d))+", "
    return output
def convertime(s):
    dt = datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ")
    formatted = dt.strftime("%I:%M:%S.%f %p UTC on %B {day}, %Y").replace(
        "{day}", str(dt.day) + suffix(dt.day)
    )
    return formatted

def formatduration(seconds: int) -> str:
    intervals = [
        ('week', 7 * 24 * 60 * 60),
        ('day', 24 * 60 * 60),
        ('hour', 60 * 60),
        ('min', 60),
        ('sec', 1),
    ]

    parts = []
    for name, count in intervals:
        value = seconds // count
        if value:
            seconds %= count
            unit = f"{value} {name}" + ("s" if value > 1 else "")
            parts.append(unit)

    if not parts:
        return "0 secs"
    elif len(parts) == 1:
        return parts[0]
    elif len(parts) == 2:
        return ' and '.join(parts)
    else:
        return ', '.join(parts[:-1]) + f", and {parts[-1]}"


def getcommand(thestring):
    index = thestring.lower().find('@bot')

    if index != -1:
        words = thestring[index + len('@bot'):].split()
        if len(words) >= 1:
            return ' '.join(words)

        else:
            return ""
    else:
        return "-1"


def getraw(thestring):
    index = thestring.lower().find('@bot')

    if index != -1:
        words = thestring[index + len('@bot'):]
        if len(words) >= 1:
            return words

        else:
            return ""
    else:
        return "-1"


def pmcommand(thestring):
    index = thestring.lower().find('@bot')
    if index != -1:
        words = thestring[index + len('@bot'):].split()
        if len(words) > 0:
            return thestring[index + len('@bot'):].strip()
        else:
            return ""
    else:
        return "-1"


def getuser(thestring):
    thestring = thestring.text
    return thestring.split('\n')[1]





def defaultresponse(response, chatpm, topic_content=None):
    x=random.randint(1,1000000)
    topiccontent = f"**[AUTOMATED]**\n There is a bug in the bot's code. The output is blank, and therefore triggered this message for error prevention. [details=\"DEBUG\"] defaultresponse({response},{chatpm})[/details]"
    if response == 0:
        if chatpm:
            topic_content.send_keys("**[AUTOMATED]**\n Hello!\n")
        else:
            topiccontent = f"**[AUTOMATED]**\n Hello!\n[details=\"tip\"] To find out what I can do, say `@bot help` or `@bot display help`.[/details] \n<font size={x}>"
    elif response == 1:
        if chatpm:
            topic_content.send_keys("**[AUTOMATED]**\n Hi!\n")
        else:
            topiccontent = f"**[AUTOMATED]**\n Hi!\n[details=\"tip\"] To find out what I can do, say `@bot help` or `@bot display help`.[/details] \n<font size={x}>"

    elif response == 2:
        if not chatpm:
            topiccontent = f"**[AUTOMATED]**\n How dare you ping me\n[details=\"tip\"] To find out what I can do, say `@bot help` or `@bot display help`.[/details] \n<font size={x}>"

        else:
            topic_content.send_keys(
                "**[AUTOMATED]**\n How dare you ping me\n")
    elif response == 3:
        if not chatpm:
            topiccontent = f"**[AUTOMATED]**\n I want to take over the world!\n[details=\"tip\"] To find out what I can do, say `@bot help` or `@bot display help`.[/details] \n<font size={x}>"

        else:
            topic_content.send_keys(
                "**[AUTOMATED]**\n I want to take over the world!\n")
    if not chatpm:
        return topiccontent
    

def changeauto(chatpm, topic_content, reqs, topicid, user, Keys):
    if chatpm:
        topic_content.send_keys("**[AUTOMATED]**")
        topic_content.send_keys(Keys.ENTER)
        topic_content.send_keys("`@bot auto` is not supported in chats. Sorry!")
    else:
        csrfres = reqs.get("https://x-camp.discourse.group/session/csrf.json")
        if csrfres.status_code != 200:
            print("Failed to fetch CSRF token:", csrfres.status_code)
            print(csrfres.text)
            exit()
        csrftoken = csrfres.json().get("csrf")
        if not csrftoken:
            print("CSRF token missing in response.")
            exit()
        reqs.headers.update(
            {
                "X-CSRF-Token": csrftoken,
                "Content-Type": "application/json",
                "Referer": f"https://x-camp.discourse.group/t/{topicid}",
            }
        )
        verireq = reqs.get(f"https://x-camp.discourse.group/t/{topicid}.json").json()[
            "post_stream"
        ]["posts"][0]["username"]
        if user == verireq:
            # bot auto logic
            autotopics = db["autotopics"]
            if str(topicid) in autotopics:
                if autotopics[str(topicid)] == True:
                    db["autotopics"][str(topicid)] = False
                    topiccontent = "**[AUTOMATED]**\nAuto mode has been **DISABLED**."
                else:
                    db["autotopics"][str(topicid)] = True
                    topiccontent = "**[AUTOMATED]**\nAuto mode has been **ENABLED**."
            else:
                db["autotopics"][str(topicid)] = True
                topiccontent = "**[AUTOMATED]**\nAuto mode has been **ENABLED**."
        else:
            topiccontent = "**[AUTOMATED]**\nYou are not the creator of this topic."
        return topiccontent

def changelog(chatpm, topic_content, Keys):
    x = random.randint(1,1000000)
    readme=requests.get("https://raw.githubusercontent.com/LiquidPixel101/Bot/main/README.md").text
    changelog_marker = "## Changelog"
    if changelog_marker in readme:
        changelog = readme.split(changelog_marker, 1)[1]
        changetext=changelog.strip()
    else:
        changetext="Changelog section not found."
                
    if chatpm:
        changetext="\n".join(changetext.split("\n")[1:4])
        topic_content.send_keys("**[AUTOMATED]**")
        topic_content.send_keys(Keys.ENTER)
        time.sleep(0.1)
        topic_content.send_keys(Keys.ENTER)
        topic_content.send_keys(f"[b]Current (Running) Version: {db['version']}[/b]")
        topic_content.send_keys(Keys.ENTER)
        time.sleep(0.1)
        topic_content.send_keys(Keys.ENTER)
        topic_content.send_keys(f"[b]Last Recorded Change:[/b]")
        topic_content.send_keys(Keys.ENTER)
        time.sleep(0.1)
        topic_content.send_keys(Keys.ENTER)
        for part in changetext.split("\n"):
            topic_content.send_keys(part)
            topic_content.send_keys(Keys.SHIFT, Keys.ENTER)
        topic_content.send_keys(Keys.ENTER)
        time.sleep(0.1)
        topic_content.send_keys(Keys.ENTER)
    else:
        topiccontent=f"**[AUTOMATED]**\n# Current (Running) Version: {db['version']}\n## Changelog:\n\n{changetext}\n<font size={x}>"
        return topiccontent

def about(chatpm, topic_content, Keys):
    x = random.randint(1,1000000)
    if chatpm:
        topic_content.send_keys("**[AUTOMATED]**")
        topic_content.send_keys(Keys.ENTER)
        time.sleep(0.1)
        topic_content.send_keys(Keys.ENTER)
        topic_content.send_keys("`@bot about` is not supported in chats. Sorry!")
    else:
        readmeog = requests.get(
            "https://raw.githubusercontent.com/LiquidPixel101/Bot/main/README.md"
        ).text
        if "## Changelog" in readmeog:
            readme = readmeog.split("## Changelog", 1)[0].rstrip()
            changelog = readmeog.split("## Changelog", 1)[1]
            changetext = changelog.strip()
        readme = readme.replace(
            "botpfp.jpg",
            "https://sea2.discourse-cdn.com/flex020/user_avatar/x-camp.discourse.group/bot/288/7873_2.png",
        )
        readme = readme.replace(
            "[ethandacat](https://github.com/ethandacat)", "@<aaa>e"
        )
        readme = readme.replace("<br>", "\n")
        readme = readme.replace("\n\n", "\n")
        topiccontent = "**[AUTOMATED]**\n"
        topiccontent += readme + "\n## Changelog" + changetext + f"\n<font size={x}>"
        return topiccontent
