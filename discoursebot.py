import time
import random
import os
import re
import json
import requests
import calendar
import google.generativeai as genai
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException as stalerr
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementClickInterceptedException as ecie
from selenium.webdriver.chrome.service import Service

genai.configure(api_key=os.environ['GOOGLE_AI_API_KEY'])
model = genai.GenerativeModel('gemini-2.0-flash-exp')
chat = model.start_chat()


def getpost(link):
    match = re.search(r'(\d+)$', link)
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

def getcommand(thestring):
    thestring = thestring.text
    index = thestring.lower().find('@bot')
    if index != -1:
        words = thestring[index + len('@bot'):].split()
        if len(words) > 1:
            return ' '.join(words[:-1])
        elif len(words) == 1:
            return ""
        else:
            return ""
    else:
        return "-1"


def pmcommand(thestring):
    thestring = thestring.text
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
    thestring=thestring.text
    return thestring.split('\n')[1]
def defaultresponse(response, chatpm):
    if response == 1:
        if chatpm:
            topic_content.send_keys(f"**[AUTOMATED]**\n Hi!\n")
        else:
            topic_content.send_keys(
                f"**[AUTOMATED]**\n Hello!\n[details=\"tip\"] To find out what I can do, say `@bot help` or `@bot display help`.[/details] \n<font size={x}>"
            )

    elif response == 2:
        if not chatpm:
            topic_content.send_keys(
                f"**[AUTOMATED]**\n How dare you ping me\n[details=\"tip\"] To find out what I can do, say `@bot help` or `@bot display help`.[/details] \n<font size={x}>"
            )
        else:
            topic_content.send_keys(
                f"**[AUTOMATED]**\n How dare you ping me\n")
    elif response == 3:
        if not chatpm:
            topic_content.send_keys(
                f"**[AUTOMATED]**\n I want to take over the world!\n[details=\"tip\"] To find out what I can do, say `@bot help` or `@bot display help`.[/details] \n<font size={x}>"
            )
        else:
            topic_content.send_keys(
                f"**[AUTOMATED]**\n I want to take over the world!\n")


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

# Main loop
while True:
    profilebutton = WebDriverWait(browser, 10).until(
        ec.element_to_be_clickable((By.ID, 'toggle-current-user')))
    profilebutton.click()
    entersummary = WebDriverWait(browser, 10).until(
        ec.element_to_be_clickable((By.ID, 'user-menu-button-profile')))
    entersummary.click()
    entersummary2 = WebDriverWait(browser, 10).until(
        ec.element_to_be_clickable((By.CLASS_NAME, 'summary')))
    entersummary2.click()
    notificationpage = WebDriverWait(browser, 10).until(
        ec.element_to_be_clickable((By.CLASS_NAME, 'user-nav__notifications')))
    notificationpage.click()
    try:
        selectfilter = WebDriverWait(browser, 10).until(
            ec.element_to_be_clickable(
                (By.CSS_SELECTOR, 'summary[data-name="All"]')))
    except TimeoutException:
        browser.refresh()
        selectfilter = WebDriverWait(browser, 10).until(
            ec.element_to_be_clickable(
                (By.CSS_SELECTOR, 'summary[data-name="All"]')))
    selectfilter.click()
    selectunread = WebDriverWait(browser, 10).until(
        ec.element_to_be_clickable(
            (By.CSS_SELECTOR, 'li[data-name="Unread"]')))
    selectunread.click()

    elementfound = False
    chatpm = False
    
    while not elementfound:
        try:
            selectmention = WebDriverWait(browser, 3).until(
                ec.element_to_be_clickable(
                    (By.CSS_SELECTOR, "li.notification.unread.mentioned a")))
            elementfound = True
            user=WebDriverWait(selectmention, 2).until(ec.element_to_be_clickable((By.CSS_SELECTOR,"span.item-label"))).text
            #print(user)
            thelink = selectmention.get_attribute("href")
            selectmention.click()
            break

        except stalerr:
            print("StaleElementReferenceException encountered. Retrying...")
            browser.refresh()
            elementfound = False
            continue;
        except TimeoutException:
            try:
                selectchat = WebDriverWait(browser, 2).until(
                    ec.element_to_be_clickable(
                        (By.CSS_SELECTOR,
                         "li.notification.unread.chat-mention a")))
                user=WebDriverWait(selectchat, 2).until(ec.element_to_be_clickable((By.CSS_SELECTOR,"span.item-label"))).text
                #print(user)
                elementfound = True
                chatpm = True
                thelink = selectchat.get_attribute("href")
                #print("thelink=", str(thelink))
                selectchat.click()
                break
            except stalerr:
                browser.refresh()
            except TimeoutException:
                #print("Try again")
                browser.refresh()
    postnum = getpost(thelink)
   
    if not chatpm:
        while 1:
            try:

                reply = WebDriverWait(browser, 10).until(
                    ec.element_to_be_clickable(
                        (By.CSS_SELECTOR,
                         f'article#post_{postnum} button.post-action-menu__reply')))
                #browser.execute_script("arguments[0].scrollIntoView();", reply)
                reply.click()
                break
            except Exception as e:
                print(f"Some error occured. \n {e}")
                browser.refresh()

        topic_content = WebDriverWait(browser, 10).until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                "textarea[aria-label='Type here. Use Markdown, BBCode, or HTML to format. Drag or paste images.']"
            )))
    else:
        postcontent = WebDriverWait(browser, 10).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, f"div[data-id='{postnum}'] div.chat-message-text")))
        try:
            ActionChains(browser).move_to_element(postcontent).perform()
            ActionChains(browser).move_to_element(postcontent).perform()
            reply = WebDriverWait(browser, 10).until( ec.element_to_be_clickable((By.CSS_SELECTOR,f'div[data-id="{postnum}"] button.reply-btn')))
            reply.click()
        except Exception:
            print("Reply button did not work.")
        topic_content = WebDriverWait(browser, 10).until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                "textarea[class='ember-text-area ember-view chat-composer__input']")))
    print(thelink)
    
    backtrack=postnum
    if not chatpm:
        postcontent = WebDriverWait(browser, 10).until(
            ec.presence_of_element_located((By.ID, f"post_{postnum}")))
    else:
        postcontent = WebDriverWait(browser, 10).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, f"div[data-id='{postnum}'] div.chat-message-text")))
        chatmessage = WebDriverWait(browser, 10).until(
            ec.presence_of_element_located(
                (By.CSS_SELECTOR, f"div[data-id='{postnum}']")))
    #print(postcontent.text)
    #print(chatmessage.text)
    command = getcommand(postcontent) if not chatpm else pmcommand(postcontent)
    
    print(command)
    x = random.randint(1, 1000000)
    if (command=="-1"):
        if chatpm:
            topic_content.send_keys(f"**[AUTOMATED]**")
            topic_content.send_keys(Keys.ENTER)
            topic_content.send_keys(f"I did not get your message. This could be because you deleted your post before I could read it.")
            topic_content.send_keys(Keys.ENTER)
        else:
            topic_content.send_keys(
                f"**[AUTOMATED]** \n\nI did not get your message. This could be because you mentioned `@all`.\n\n<font size={x}>")
    if (command == ""):
        response = random.randint(0, 3)
        x = random.randint(1, 1000000)
        defaultresponse(response, chatpm)
    else:  #--------------------------------------------------------
        # print(command)
        command = command.split()
        response = random.randint(0, 3)

        x = random.randint(1, 100000)
        if command[0] == "say" and len(command) >= 2:
            del command[0]
            parrot = ' '.join(command)
            parrot=checkbmp(parrot)
            if chatpm:
                topic_content.send_keys(f"**[AUTOMATED]** \n\n {parrot}")
                topic_content.send_keys(Keys.ENTER)
                topic_content.send_keys(Keys.ENTER)
                topic_content.send_keys(Keys.ENTER)
            else:
                topic_content.send_keys(
                    f"**[AUTOMATED]** \n{parrot}<font size={x}>")

        elif (len(command)>1 and command[0] == "display" and command[1] == "help") or (command[0]=="help"):
            if chatpm:
                topic_content.send_keys(
                    f"**[AUTOMATED]** \n\nI currently know how to do the following things:"
                )
                topic_content.send_keys(Keys.ENTER)
                topic_content.send_keys(Keys.ENTER)
                topic_content.send_keys(
                    f"`@bot ai [PROMPT]`: Outputs a Gemini 2.0-Flash Experimental response with the prompt of everything after the `ai`."
                )
                topic_content.send_keys(Keys.ENTER)
                topic_content.send_keys(f"`@bot say [PARROTED TEXT]`: Parrots everything after the `say`.")
                topic_content.send_keys(Keys.ENTER)
                topic_content.send_keys(f"`@bot xkcd`: Generates a random [xkcd](https://xkcd.com) comic.")
                topic_content.send_keys(Keys.ENTER)
                topic_content.send_keys(f"`@bot xkcd last` or `@bot xkcd latest`: Outputs the most recent [xkcd](https://xkcd.com) comic.")
                topic_content.send_keys(Keys.ENTER)
                topic_content.send_keys(f"`@bot xkcd blacklist`: Outputs all of the blacklisted XKCD comic ID's.")
                topic_content.send_keys(Keys.ENTER)
                topic_content.send_keys(f"`@bot xkcd comic [ID HERE]`: Gives you the xkcd comic with the ID along with some info on the comic.")
                topic_content.send_keys(Keys.ENTER)
                topic_content.send_keys(f"More coming soon! ")
                topic_content.send_keys(Keys.ENTER)
                topic_content.send_keys(Keys.ENTER)
                topic_content.send_keys(f"For more information, visit [the github page for bot](https://github.com/LiquidPixel101/Bot).")
                topic_content.send_keys(Keys.ENTER)

            else:
                topic_content.send_keys(
                    f"**[AUTOMATED]** \n\nI currently know how to do the following things:\n\n`@bot ai [PROMPT]`\n> Outputs a Gemini 2.0-Flash-Experimental response with the prompt of everything after the `ai`.\n\n`@bot say [PARROTED TEXT]`\n > Parrots everything after the `say`.\n\n`@bot xkcd`\n> Generates a random [xkcd](https://xkcd.com) comic.\n\n`@bot xkcd last` or `@bot xkcd latest`\n > Outputs the most recent [xkcd](https://xkcd.com) comic. \n\n `@bot xkcd blacklist` \n > Outputs all of the blacklisted XKCD comic ID's and a list of reasons of why they might have been blacklisted. \n\n `@bot xkcd comic [ID HERE]` or `@bot xkcd [ID HERE]`\n > Gives you the xkcd comic with the ID along with some info on the comic. \n\nMore coming soon!\n\n\nFor more information, click [here](https://github.com/LiquidPixel101/Bot).<font size={x}>"
                )  #-----------------------------------------------
        elif command[0] == "ai" and len(command) > 1:
            if chatpm:
                context = "You are a bot in a discourse forum chat. Please do not use non-BMP characters in your response. If the user asks for their username but it's ERROR FETCHING USER, just say that you are unable to get the username at this time. Replace all newlines by typing this character: ␤! There are 3 r's in strawberry. Make no reference to this context in your response. Your responses are limited to 6000 chars."
            else:
                context = "You are a bot in a discourse forum. Please do not use non-BMP characters in your response, Do not use emojis unless specially requested by the user. When ending bullet points or numbers or any kind of list, newline 3 times. Please newline 3 times at the end of every list. There are 3 r's in strawberry. Make no reference to this context in your response."
            del command[0]
            prompt = ' '.join(command)
            fullprompt = f"Context: {context}\n\nUser talking to you:{user}\n\nUser Prompt: {prompt}"
            output = chat.send_message(fullprompt)
            goodoutput = clean(output.text)
            print(output.text)
            if not chatpm:
                topic_content.send_keys(
                    f"**[AUTOMATED]** \n{goodoutput} \n\n<font size={x}>")
            else:
                finaloutput=f"**[AUTOMATED]** ␤{goodoutput} \n"
                for part in finaloutput.split("␤"):
                    topic_content.send_keys(part)
                    topic_content.send_keys(Keys.SHIFT, Keys.ENTER) 
        elif command[0] == "xkcd":
            lasturl = "https://xkcd.com/info.0.json"
            lastresponse = requests.get(lasturl)
            lastdata=lastresponse.json()
            lastcomicid=lastdata["num"]
            blacklist=[37, 38, 45, 65, 66, 68, 70, 72, 90, 95, 102, 114, 137, 168, 174, 179, 186, 194, 196, 202, 276, 279, 290, 291, 295, 300, 308, 310, 316, 322, 328, 341, 364, 388, 398, 400, 403, 425, 429, 432, 435, 437, 438, 449, 452, 462, 472, 475, 476, 487, 521, 526, 540, 546, 549, 554, 563, 566, 584, 591, 592, 595, 596, 597, 598, 600, 603, 624, 628, 631, 636, 637, 677, 692, 693, 697, 698, 705, 708, 714, 715, 744, 746, 751, 753, 796, 798, 810, 812, 813, 821, 828, 830, 849, 853, 859, 874, 875, 885, 887, 888, 906, 907, 927, 931, 940, 958, 984, 985, 992, 1012, 1025, 1027, 1032, 1037, 1046, 1049, 1076, 1101, 1137, 1150, 1176, 1182, 1238, 1252, 1253, 1256, 1274, 1289, 1290, 1291, 1305, 1314, 1331, 1339, 1357, 1383, 1431, 1458, 1462, 1491, 1504, 1564, 1617, 1634, 1646, 1647,404,1848]
            blacklist.sort()
            isblacklist=False
            iscomic=False
            dontoutput=False
            if len(command)>1:
                if command[1] == "last" or command[1]=="latest":    
                    comicurl=lastdata["img"]
                    xkcdlink = 'https://xkcd.com/' + str(lastcomicid)
                elif command[1] == "blacklist":
                    isblacklist=True
                    theblacklist=", ".join(map(str, blacklist))   
                    theblacklist=theblacklist+"."
                elif (isnumber(command[1])):
                    if float(command[1])>0 and float(command[1])<=lastcomicid and isinteger(command[1]) and float(command[1])!=404:
                        if (int(command[1]) in blacklist):
                            dontoutput=True
                            if chatpm:
                                topic_content.send_keys(f"**[AUTOMATED]**")
                                topic_content.send_keys(Keys.ENTER)
                                topic_content.send_keys("This xkcd comic is in the blacklist. Sorry!")
                            else:
                                topic_content.send_keys(f"**[AUTOMATED]**\nThis xkcd comic is in the blacklist. \n\nXKCD comics can be blacklisted for:\n* Unsupported characters in title.\nNonexistent comic. \nInappropriate words.\n\n <font size={x}>")
                        else:
                            comic = 'https://xkcd.com/' + command[1] + '/info.0.json'
                            response=requests.get(comic)
                            data=response.json()
                            xkcdlink='https://xkcd.com/' + command[1]
                            iscomic=1
                    else:
                        dontoutput=True
                        if chatpm:
                            topic_content.send_keys(f"**[AUTOMATED]**")
                            topic_content.send_keys(Keys.ENTER)
                            topic_content.send_keys(f"{command[1]} is not a valid XKCD comic ID. This is because a comic with this ID does not exist.")
                        else:
                            topic_content.send_keys(f"**[AUTOMATED]**\n{command[1]} is not a valid XKCD comic ID. This is because a comic with this ID does not exist. <font size={x}>")
                elif command[1]=="comic":
                    if len(command)==2:
                        dontoutput=True
                        if chatpm:
                            topic_content.send_keys(f"**[AUTOMATED]**")
                            topic_content.send_keys(Keys.ENTER)
                            topic_content.send_keys("It seems like you forgot to type in your ID for the xkcd. For more information, say `@bot help` or `@bot display help`.")
                        else:
                            topic_content.send_keys("**[AUTOMATED]**\nIt seems like you forgot to type in your ID for the xkcd.\n For more information, say `@bot help` or `@bot display help`.\n<font size={x}>")
                    elif len(command)>=3:
                        if (isnumber(command[2])):
                            if float(command[2])>0 and float(command[2])<=lastcomicid and isinteger(command[2]) and float(command[2])!=404:
                                if (int(command[2]) in blacklist):
                                    dontoutput=True
                                    if chatpm:
                                        topic_content.send_keys(f"**[AUTOMATED]**")
                                        topic_content.send_keys(Keys.ENTER)
                                        topic_content.send_keys("This xkcd comic is in the blacklist. Sorry!")
                                    else:
                                        topic_content.send_keys(f"**[AUTOMATED]**\nThis xkcd comic is in the blacklist. \n\nXKCD comics can be blacklisted for:\n* Unsupported characters in title.\nNonexistent comic. \nInappropriate words.\n\n <font size={x}>")
                                else:
                                    comic = 'https://xkcd.com/' + command[2] + '/info.0.json'
                                    response=requests.get(comic)
                                    data=response.json()
                                    xkcdlink='https://xkcd.com/' + command[2]
                                    iscomic=1
                            else:
                                dontoutput=True
                                if chatpm:
                                    topic_content.send_keys(f"**[AUTOMATED]**")
                                    topic_content.send_keys(Keys.ENTER)
                                    topic_content.send_keys(f"{command[2]} is not a valid XKCD comic ID. This is because a comic with this ID does not exist.")
                                else:
                                    topic_content.send_keys(f"**[AUTOMATED]**\n{command[2]} is not a valid XKCD comic ID. This is because a comic with this ID does not exist. <font size={x}>")
                        else:
                            dontoutput=True
                            if chatpm:
                                topic_content.send_keys(f"**[AUTOMATED]**")
                                topic_content.send_keys(Keys.ENTER)
                                topic_content.send_keys(f"{command[2]} is not a valid XKCD comic ID. This is because the ID is not a number.")
                            else:
                                topic_content.send_keys(f"**[AUTOMATED]**\n{command[2]} is not a valid XKCD comic ID. This is because the ID is not a number.")
                else:
                    rand = random.randint(1, lastcomicid)
                    while rand in blacklist:
                        rand = random.randint(1, lastcomicid)
                    comic = 'https://xkcd.com/' + str(rand) + '/info.0.json'
                    response=requests.get(comic)
                    data=response.json()
                    comicurl=data["img"]
                    xkcdlink = 'https://xkcd.com/' + str(rand)
            else:
                rand = random.randint(1, lastcomicid)
                while rand in blacklist:
                    rand = random.randint(1, lastcomicid)
                comic = 'https://xkcd.com/' + str(rand) + '/info.0.json'
                response=requests.get(comic)
                data=response.json()
                comicurl=data["img"]
                xkcdlink = 'https://xkcd.com/' + str(rand)
            
            #print(data)
            #print(srce)
            #src2 = str(srce)
            #================================================================
            if not dontoutput:
                if (isblacklist):
                    if not chatpm:
                        topic_content.send_keys(f"**[AUTOMATED]**\nCurrently, the following {len(blacklist)} XKCD comics are blacklisted:\n{theblacklist}\n\nXKCD comics can be blacklisted for:\n* Unsupported characters in title\nNonexistent comic \nInappropriate words\n\n<font size={x}>")
                    else:
                        topic_content.send_keys(f"**[AUTOMATED]**")
                        topic_content.send_keys(Keys.ENTER)
                        topic_content.send_keys(f"Currently, the following {len(blacklist)} XKCD comics are blacklisted:")
                        topic_content.send_keys(Keys.SHIFT, Keys.ENTER)
                        topic_content.send_keys(theblacklist)
                elif (iscomic):
                    if chatpm:
                        topic_content.send_keys(f"**[AUTOMATED]**")
                        topic_content.send_keys(Keys.ENTER)
                        topic_content.send_keys(f"**{data['safe_title']}** - XKCD {data['num']}")
                        topic_content.send_keys(Keys.SHIFT, Keys.ENTER) 
                        time.sleep(0.1)
                        topic_content.send_keys(Keys.SHIFT, Keys.ENTER) 
                        topic_content.send_keys(f"Published {calendar.month_name[int(data['month'])]} {data['day']}, {data['year']}")
                        topic_content.send_keys(Keys.SHIFT, Keys.ENTER) 
                        time.sleep(0.1)
                        topic_content.send_keys(Keys.SHIFT, Keys.ENTER) 
                        topic_content.send_keys(f"[spoiler]![]({data['img']})[/spoiler]")
                        topic_content.send_keys(Keys.SHIFT, Keys.ENTER) 
                        topic_content.send_keys(f"*Link: {xkcdlink}*")
                        topic_content.send_keys(Keys.SHIFT, Keys.ENTER) 
                        time.sleep(0.1)
                        topic_content.send_keys(Keys.SHIFT, Keys.ENTER) 
                        topic_content.send_keys(f"**WARNING: SOME XKCD COMICS MAY NOT BE APPROPRIATE FOR ALL AUDIENCES. PLEASE VIEW THE ABOVE AT YOUR OWN RISK!**")
                        topic_content.send_keys(Keys.ENTER) 
                        time.sleep(0.1)
                        topic_content.send_keys(Keys.ENTER) 
                        topic_content.send_keys(f"Description: {data['alt']}")
                        
                        if data['transcript']!="":
                            topic_content.send_keys(Keys.ENTER) 
                            time.sleep(0.1)
                            topic_content.send_keys(Keys.ENTER) 
                            topic_content.send_keys(f"[u]**Transcript:**[/u]")
                            topic_content.send_keys(Keys.SHIFT, Keys.ENTER)
                            time.sleep(0.1)
                            topic_content.send_keys(Keys.SHIFT, Keys.ENTER)
                            data['transcript']=dellast(data['transcript'])
                            topic_content.send_keys(f"```txt")
                            topic_content.send_keys(Keys.SHIFT, Keys.ENTER)  
                            for part in data['transcript'].split("\n"):
                                topic_content.send_keys(part)
                                topic_content.send_keys(Keys.SHIFT, Keys.ENTER) 
                            #topic_content.send_keys(f"{data['transcript']}")
                            topic_content.send_keys(Keys.SHIFT, Keys.ENTER) 
                            topic_content.send_keys(f"```")
                            topic_content.send_keys(Keys.ENTER)
                    else:
                        if (data['transcript']==""):   
                            topic_content.send_keys(f"**[AUTOMATED]**\n\n# {data['safe_title']} - XKCD {data['num']}\n### Published {calendar.month_name[int(data['month'])]} {data['day']}, {data['year']}\n[spoiler]![]({data['img']})[/spoiler]\n*Link: {xkcdlink}*\n\n##### **WARNING: SOME XKCD COMICS MAY NOT BE APPROPRIATE FOR ALL AUDIENCES. PLEASE VIEW THE ABOVE AT YOUR OWN RISK!** \n\n---\n\n**Description:**\n {data['alt']}\n\n<font size={x}>")
                        else:
                            data['transcript']=dellast(data['transcript'])
                            topic_content.send_keys(f"**[AUTOMATED]**\n\n# {data['safe_title']} - XKCD {data['num']}\n### Published {calendar.month_name[int(data['month'])]} {data['day']}, {data['year']}\n[spoiler]![]({data['img']})[/spoiler]\n*Link: {xkcdlink}*\n\n##### **WARNING: SOME XKCD COMICS MAY NOT BE APPROPRIATE FOR ALL AUDIENCES. PLEASE VIEW THE ABOVE AT YOUR OWN RISK!** \n\n---\n\n**Description:**\n {data['alt']}\n\n---\n\n[details=Transcript]\n```txt\n{data['transcript']}\n```\n[/details]\n\n<font size={x}>")
                else:
                    if not chatpm:
                        topic_content.send_keys(f"**[AUTOMATED]** \n[spoiler]![]({comicurl})[/spoiler]\n*source: {xkcdlink}*\n\n**WARNING: SOME XKCD COMICS MAY NOT BE APPROPRIATE FOR ALL AUDIENCES. PLEASE VIEW THE ABOVE AT YOUR OWN RISK!** \n<font size={x}>")
                    else:
                        topic_content.send_keys(f"**[AUTOMATED]** \n[spoiler]![]({comicurl})[/spoiler]\n\n*source: {xkcdlink}*\n \n")
                        topic_content.send_keys(Keys.ENTER)
                        topic_content.send_keys(f"**WARNING: SOME XKCD COMICS MAY NOT BE APPROPRIATE FOR ALL AUDIENCES. PLEASE VIEW THE ABOVE AT YOUR OWN RISK!**")
        else:
            defaultresponse(response, chatpm)
    if not chatpm:
        reply_button = WebDriverWait(browser, 10).until(
            ec.element_to_be_clickable((
                By.CSS_SELECTOR,
                "button.btn.btn-icon-text.btn-primary.create[title='Or press Ctrl+Enter']"
            )))
        reply_button.click()
    else:
        try:
            reply_button = WebDriverWait(browser, 10).until(ec.element_to_be_clickable((By.CLASS_NAME, "chat-composer-button.-send")))
            reply_button.click()
        except TimeoutException:
            time.sleep(0.5)
            try:
                reply_button = WebDriverWait(browser, 10).until(ec.element_to_be_clickable((By.CLASS_NAME, "chat-composer-button.-send")))
                reply_button.click()
            except TimeoutException:
                topic_content.send_keys(Keys.ENTER)

    time.sleep(0.002)
    browser.refresh()
    browser.get('https://x-camp.discourse.group/')
