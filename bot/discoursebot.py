import calendar
import os
import random
import re
import time
import json
from datetime import datetime
import requests
from replit import db
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
import ai
import run
import xkcd
import support
import display
from utils import *
import autobahn


options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--shm-size=1g")
options.add_argument('--disable-gpu')
options.add_argument("--headless")
options.add_argument('--disable-software-rasterizer')
options.add_argument('--remote-debugging-port=9222')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('--disable-infobars')
options.add_argument('--window-size=1920,1080')
options.add_argument('--disable-extensions')
options.add_argument('--start-maximized')
email = os.environ['EMAIL']
password = os.environ['PASSWORD']

#chromedriver_path = "/nix/store/3qnxr5x6gw3k9a9i7d0akz0m6bksbwff-chromedriver-125.0.6422.141/bin/chromedriver"
#service = Service(chromedriver_path)
browser = webdriver.Chrome(options=options)
browser.get('https://x-camp.discourse.group/')

# Login
WebDriverWait(browser,
              10).until(ec.presence_of_element_located(
                  (By.ID, "username"))).send_keys(email)
WebDriverWait(browser,
              10).until(ec.presence_of_element_located(
                  (By.ID, "password"))).send_keys(password)
signin = WebDriverWait(browser, 10).until(
    ec.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
signin.click()
WebDriverWait(browser, 10).until(ec.presence_of_element_located((By.ID, "toggle-current-user")))
time.sleep(1)
browser.refresh()
reqs = requests.Session()
for cookie in browser.get_cookies():
    reqs.cookies.set(cookie['name'], cookie['value'])
posturl = 'https://x-camp.discourse.group/posts.json'
# Main loop
while True:
    chatpm = False
    perm = False
    postid = 0
    autoloop = 1
    elementfound = False
    autotopics = db.get("autotopics", {})
    enabled_autos = [tid for tid, enabled in autotopics.items() if enabled]
    while not elementfound:
        notifdata = reqs.get(
            "https://x-camp.discourse.group/notifications.json")
        if notifdata.status_code != 200:
            print("Bad status code:", notifdata.status_code)
            time.sleep(1)
            notifdata = reqs.get("https://x-camp.discourse.group/notifications.json")
        notifdata = notifdata.json()
        for notif in notifdata['notifications']:
            notifid = notif['id']
            if notif['read'] or notifid in db["notifs"]:
                reqs.post(
                    "https://x-camp.discourse.group/notifications/mark-read",
                    data={"id": notifid})
                time.sleep(0.5)
                break
            if notif['read'] == False and notif['notification_type'] in [
                    1, 6, 29
            ]:
                notif_type = notif['notification_type']
                if notif_type == 1:
                    user = notif["data"]["display_username"]
                    thelink = f"https://x-camp.discourse.group/t/{notif['topic_id']}/{notif['post_number']}"
                    topicid = notif['topic_id']
                    postid = notif['data']['original_post_id']
                    print(postid)
                    postdatae = reqs.get(
                        f"https://x-camp.discourse.group/posts/{postid}.json"
                    ).json()
                    postnum = postdatae["post_number"]

                elif notif_type == 29:
                    user = notif["data"]["mentioned_by_username"]
                    thelink = f"https://x-camp.discourse.group/chat/channel/{notif['data']['chat_channel_id']}/{notif['data']['chat_message_id']}"
                    channelid = notif['data']['chat_channel_id']
                    postnum = notif['data']['chat_message_id']
                    chatpm = True
                    reqs.post(
                        "https://x-camp.discourse.group/notifications/mark-read",
                        data={"id": notifid})
                elif notif_type == 6:
                    user = notif["data"]["display_username"]
                    thelink = f"https://x-camp.discourse.group/t/{notif['topic_id']}/{notif['post_number']}"
                    topicid = notif['topic_id']
                    postid = notif['data']['original_post_id']
                    postdatae = reqs.get(
                        f"https://x-camp.discourse.group/posts/{postid}.json"
                    ).json()
                    postnum = postdatae["post_number"]
                    perm = True
                elementfound = True
                db["notifs"].append(notifid)
        # if auto
        if autoloop%5==0:
            for aatopic in enabled_autos:
                newposts = autobahn.get_new_posts(aatopic)
                if not newposts[1] == []:
                    # actual auto stuff
                    autobahn.autobahn(aatopic,newposts[0], reqs, topicid, BOT_USERNAME)
        autoloop+=1
    if chatpm:
        browser.get(thelink)
        browser.refresh()

    print(postnum)
    if not chatpm:
        topiccontent = "**[AUTOMATED]**\n There was a bug in the bot's code. The output is blank, and therefore triggered this message for error prevention. [details=\"DEBUG\"] GeneralError[/details]"
    else:
        try:
            ActionChains(browser).move_to_element(postcontent).perform()
            ActionChains(browser).move_to_element(postcontent).perform()
            reply = WebDriverWait(browser, 10).until(
                ec.element_to_be_clickable(
                    (By.CSS_SELECTOR,
                     f'div[data-id="{postnum}"] button.reply-btn')))
            reply.click()
        except Exception:
            print("Reply button did not work.")
        try:
            topic_content = WebDriverWait(browser, 10).until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    "textarea[class='ember-text-area ember-view chat-composer__input']"
                )))
        except Exception:
            print("The regular button also didn't work. Sleeping 5 seconds...")
            time.sleep(5)
            topic_content = WebDriverWait(browser, 10).until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    "textarea[class='ember-text-area ember-view chat-composer__input']"
                )))
    print(thelink)

    if not chatpm:
        #postcontent = WebDriverWait(browser, 10).until(ec.presence_of_element_located((By.ID, f"post_{postnum}")))
        postdata = reqs.get(
            f"https://x-camp.discourse.group/posts/{postid}.json").json()
        postcontent = postdata["raw"]
    else:
        postcontent = 0
        messagedata = reqs.get(
            f"https://x-camp.discourse.group/chat/api/channels/{channelid}/messages.json"
        ).json()
        #print(messagedata)
        for msg in messagedata["messages"]:
            if msg["id"] == postnum:
                postcontent = msg["message"]
        if postcontent == 0:
            browser.refresh()
            break
        chatmessage = postcontent
    print(postcontent)
    #print(chatmessage.text)
    command = getcommand(postcontent) if not chatpm else pmcommand(postcontent)
    rawpost = getraw(postcontent)
    print(command)
    x = random.randint(1, 1000000)
    if (command == "-1"):
        if perm:
            browser.refresh()
            browser.get('https://x-camp.discourse.group/')
            continue
        if chatpm:
            topic_content.send_keys("**[AUTOMATED]**")
            topic_content.send_keys(Keys.ENTER)
            topic_content.send_keys(
                "I did not get your message. This could be because you mentioned `@all`."
            )
            topic_content.send_keys(Keys.ENTER)
        else:
            topiccontent = f"**[AUTOMATED]** \n\nI did not get your message. This could be because you deleted your post before I could read it.\n\n<font size={x}>"
    if (command == ""):
        response = random.randint(0, 3)
        x = random.randint(1, 1000000)
        if chatpm:
            defaultresponse(response, chatpm, topic_content)
        else:
            topiccontent = defaultresponse(response, chatpm)

    else:  #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        print(command)
        command = command.split()
        response = random.randint(0, 3)

        x = random.randint(1, 1000000)
        if command[0].lower() == "say" and len(command) >= 2:
            del command[0]
            #print("rawpost",rawpost)
            parrot = ' '.join(command) if chatpm else rawpost[5:]
            parrot = checkbmp(parrot)
            if chatpm:
                topic_content.send_keys(f"**[AUTOMATED]** \n\n {parrot}")
                topic_content.send_keys(Keys.ENTER)
                topic_content.send_keys(Keys.ENTER)
                topic_content.send_keys(Keys.ENTER)
            else:
                topiccontent = f"**[AUTOMATED]** \n{parrot}<font size={x}>"
        elif command[0].lower() == "fortune":
            randomnum = random.randint(0, 19)
            fortuneans = [
                "It is certain", "It is decidedly so", "Without a doubt",
                "Yes definitely", "You may rely on it", "As I see it, yes",
                "Most likely", "Outlook good", "Yes", "Signs point to yes",
                "Reply hazy, try again", "Ask again later",
                "Better not tell you now", "Cannot predict now",
                "Concentrate and ask again", "Don’t count on it",
                "My reply is no", "My sources say no", "Outlook not so good",
                "Very doubtful"
            ]
            if chatpm:
                topic_content.send_keys("**[AUTOMATED]**")
                topic_content.send_keys(Keys.ENTER)
                topic_content.send_keys(
                    f"> :crystal_ball: {fortuneans[randomnum]}")
                topic_content.send_keys(Keys.ENTER)
            else:
                topiccontent = f"**[AUTOMATED]**\n> :crystal_ball: {fortuneans[randomnum]}\n\n<font size={x}>"

        elif (len(command) > 1 and command[0].lower() == "display"
              and command[1].lower() == "help") or (command[0].lower()
                                                    == "help"):
            display.help(chatpm, topic_content)

        elif command[0].lower() == "user":
            if chatpm:
                support.user(command, reqs, chatpm, topic_content)
            else:
                topiccontent = support.user(command, reqs, chatpm, None)
        elif command[0].lower()=="support" or command[0].lower()=="suggest":
            if chatpm:
                support.support(chatpm, topic_content, reqs, user, command, rawpost)
            else:
                topiccontent = support.support(chatpm, None, reqs, user, command, rawpost)

        elif (command[0].lower()=="roll"):
            altput=""
            if len(command)>1 and command[1].isdigit():
                altput=diceroll(1,int(command[1]))
            elif len(command)>1:
                match = re.fullmatch(r'(\d+)d(\d+)', command[1])
                if match:
                    t = int(match.group(1))
                    d = int(match.group(2))
                    #print("gotheretho")
                    altput=diceroll(t,d)
                else:
                    altput="**[AUTOMATED]**\n\nPlease use the `roll` command in this format: `roll {# OF DICE}d{# OF SIDES OF EACH DICE}`.\nExample: `@bot roll 2d6`. This will roll 2 six-sided dice.\n\n Or, do `roll {# OF SIDES}`.\nExample: `@bot roll 6`: This rolls 1 six-sided die."
            #print("this is da altput:",altput)
            if chatpm:
                for part in altput.split("\n"):
                    topic_content.send_keys(part)
                    topic_content.send_keys(Keys.ENTER)
            else:
                topiccontent=altput+f"<a{random.randint(1,20000000)}>"

        elif (command[0].lower()=="about"):
            if chatpm:
                about(chatpm, topic_content, Keys)
            else:
                topiccontent = about(chatpm, None, Keys)
        
        elif (command[0].lower() == "version" or command[0].lower() == "ver" or command[0].lower() == "changelog" or command[0].lower() == "log"):
            if chatpm:
                changelog(chatpm, topic_content, Keys)
            else:
                topiccontent = changelog(chatpm, None, Keys)

        elif command[0].lower() == "ai" and len(command) > 1:
            del command[0]
            topiccontent = ai.process(' '.join(command), chatpm, reqs, user)
            if chatpm:
                for part in topiccontent.split("␤"):
                    topic_content.send_keys(part)
                    topic_content.send_keys(Keys.SHIFT, Keys.ENTER)

        elif command[0].lower() == "run":
            if chatpm:
                topic_content.send_keys("**[AUTOMATED]**")
                topic_content.send_keys(Keys.ENTER)
                topic_content.send_keys(
                    "`@bot run` is not supported in chats. Sorry!")
                topic_content.send_keys(Keys.ENTER)
            else:
                if len(command) > 1:
                    # if len(command)>2:
                    #     langcode=command[1]+" "+command[2]
                    # else:
                    #     langcode=command[1]
                    langcode = re.sub(r'^\s*\S+\s*', '', rawpost, count=1)
                    print("langcode:\n", langcode)
                    print("langcodefinish")
                    print("rawcode:", rawpost)
                    thelangcode = run.extlangcode(langcode)
                    lang = thelangcode[0]
                    code = thelangcode[1]
                    print(thelangcode)
                    codeoutput = run.run_code(code, lang)
                    print(codeoutput)
                    topiccontent = f"**[AUTOMATED]** \n{codeoutput}\n\n<font size={x}>"
                else:
                    topiccontent = f"**[AUTOMATED]** \nPlease enter the command in the format of:\n```@bot run [python/c++]\n[CODE]``` \n\n<font size={x}>"
            #topiccontent=f"**[AUTOMATED]** \n{run_code("

        elif command[0].lower() == "auto":
            changeauto(chatpm, topiccontent, reqs, topicid, user, Keys)
        
        elif command[0].lower() == "xkcd":
            topiccontent = xkcd.xkcd(command, chatpm, user)
            if chatpm:
                lines = topiccontent.split("\n")
                for line in lines:
                    topic_content.send_keys(line)
                    topic_content.send_keys(Keys.SHIFT, Keys.ENTER)
        
        else:
            if chatpm:
                defaultresponse(response, chatpm, topic_content)
            else:
                topiccontent = defaultresponse(response, chatpm)
    if not chatpm:
        print(topiccontent)
        csrfres = reqs.get('https://x-camp.discourse.group/session/csrf.json')
        if csrfres.status_code != 200:
            print('Failed to fetch CSRF token:', csrfres.status_code)
            print(csrfres.text)
            exit()
        csrftoken = csrfres.json().get('csrf')
        if not csrftoken:
            print('CSRF token missing in response.')
            exit()
        reqs.headers.update({
            'X-CSRF-Token':
            csrftoken,
            'Content-Type':
            'application/json',
            'Referer':
            f'https://x-camp.discourse.group/t/{topicid}'
        })
        payload = {'raw': topiccontent, 'topic_id': topicid}
        dastatus = reqs.post(posturl, json=payload)
        if dastatus.status_code == 200:
            print('Post successful:', dastatus.json()['id'])
        else:
            print(f'Failed to post. Status code: {dastatus.status_code}')
            print('Response:', dastatus.text)
            stufff = json.loads(dastatus.text)
            error_type = stufff.get("error_type")
            if (error_type=="rate_limit"):
                time.sleep(10)
                dastatus = reqs.post(posturl, json=payload)
                if dastatus.status_code == 200:
                    print('Post successful:', dastatus.json()['id'])
                else:
                    print(f'Failed to post. Status code: {dastatus.status_code}')
                    print('Response:', dastatus.text)

        # reply_button = WebDriverWait(browser, 10).until(
        #     ec.element_to_be_clickable((
        #         By.CSS_SELECTOR,
        #         "button.btn.btn-icon-text.btn-primary.create[title='Or press Ctrl+Enter']"
        #     )))
        # reply_button.click()
    else:
        try:
            reply_button = WebDriverWait(browser, 10).until(
                ec.element_to_be_clickable(
                    (By.CLASS_NAME, "chat-composer-button.-send")))
            reply_button.click()
        except TimeoutException:
            time.sleep(0.5)
            try:
                reply_button = WebDriverWait(browser, 10).until(
                    ec.element_to_be_clickable(
                        (By.CLASS_NAME, "chat-composer-button.-send")))
                reply_button.click()
            except TimeoutException:
                topic_content.send_keys(Keys.ENTER)

    time.sleep(0.002)
    browser.refresh()
    browser.get('https://x-camp.discourse.group/')
