import time
import random
import os
import re
import json
import requests
import google.generativeai as genai
from selenium import webdriver
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
                f"**[AUTOMATED]**\n Hello!\n[details=\"tip\"] To find out what I can do, say `@bot display help` .[/details] \n<font size={x}>"
            )

    elif response == 2:
        if not chatpm:
            topic_content.send_keys(
                f"**[AUTOMATED]**\n How dare you ping me\n[details=\"tip\"] To find out what I can do, say `@bot display help` .[/details] \n<font size={x}>"
            )
        else:
            topic_content.send_keys(
                f"**[AUTOMATED]**\n How dare you ping me\n")
    elif response == 3:
        if not chatpm:
            topic_content.send_keys(
                f"**[AUTOMATED]**\n I want to take over the world!\n[details=\"tip\"] To find out what I can do, say `@bot display help` .[/details] \n<font size={x}>"
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
#options.add_argument('--window-size=1920,1080')
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
    thelink = ""
    time.sleep(1)
    while not elementfound:
        try:
            selectmention = WebDriverWait(browser, 3).until(
                ec.element_to_be_clickable(
                    (By.CSS_SELECTOR, "li.notification.unread.mentioned a")))
            elementfound = True
            thelink = selectmention.get_attribute("href")
            selectmention.click()
            # selectchat = WebDriverWait(browser, 2).until(
            #     ec.element_to_be_clickable(
            #         (By.CSS_SELECTOR,
            #          "li.notification.unread.chat-mention a")))
            # elementfound = True
            # chatpm = True
            # thelink = selectchat.get_attribute("href")
            #print("thelink=", str(thelink))
            # selectchat.click()
            break

        except stalerr:
            print("StaleElementReferenceException encountered. Retrying...")
            browser.refresh()
        except TimeoutException:
            try:
                selectchat = WebDriverWait(browser, 2).until(
                    ec.element_to_be_clickable(
                        (By.CSS_SELECTOR,
                         "li.notification.unread.chat-mention a")))
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
    if not chatpm:
        while 1:
            try:

                reply = WebDriverWait(browser, 10).until(
                    ec.element_to_be_clickable(
                        (By.CSS_SELECTOR,
                         'button.btn.btn-icon-text.btn-primary.create')))
                browser.execute_script("arguments[0].scrollIntoView();", reply)
                reply.click()
                break
            except TimeoutException:
                browser.refresh()

        topic_content = WebDriverWait(browser, 10).until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                "textarea[aria-label='Type here. Use Markdown, BBCode, or HTML to format. Drag or paste images.']"
            )))
    else:
        topic_content = WebDriverWait(browser, 10).until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                "textarea[class='ember-text-area ember-view chat-composer__input']"
            )))
    print(thelink)
    postnum = getpost(thelink)
    backtrack=postnum
    if not chatpm:
        postcontent = WebDriverWait(browser, 10).until(
            ec.presence_of_element_located((By.ID, f"post_{postnum}")))
        user=getuser(postcontent)
    else:
        chatmessage = WebDriverWait(browser, 10).until(
            ec.presence_of_element_located(
                (By.CSS_SELECTOR, f"div[data-id='{postnum}']")))
        postcontent = WebDriverWait(browser, 10).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, f"div[data-id='{postnum}'] div.chat-message-text")))
        #print(chatmessage.get_attribute("class")) 
        theclass=chatmessage.get_attribute("class")
        classlist=theclass.split() if theclass else []
        # print(backtrack)
        # print(classlist) 
        while classlist[-1]=="-user-info-hidden":
            backtrack=backtrack-1 if backtrack is not None else None
            # print(backtrack)
            chatmessage = WebDriverWait(browser, 10).until(
                ec.presence_of_element_located(
                    (By.CSS_SELECTOR, f"div[data-id='{backtrack}']")))
            theclass=chatmessage.get_attribute("class")
            classlist=theclass.split() if theclass else []
        # thingyelement = WebDriverWait(browser, 20).until(
        #     ec.presence_of_element_located((By.CSS_SELECTOR, f'div[data-id="{backtrack}"]'))
        # )
        try:
           usercardelement=WebDriverWait(browser, 10).until(ec.presence_of_element_located((By.CSS_SELECTOR, f'div[data-id="{backtrack}"] .chat-user-avatar a.chat-user-avatar__container')))
           user=usercardelement.get_attribute("data-user-card")
        except TimeoutException:
            try:
                usercardelement=WebDriverWait(browser, 10).until(ec.presence_of_element_located((By.CSS_SELECTOR, f'div[data-id="{backtrack}"] .chat-user-avatar a.chat-user-avatar__container')))
                user=usercardelement.get_attribute("data-user-card")
            except TimeoutException:
                user="ERROR FETCHING USER"
        # usercardelement = WebDriverWait(browser, 10).until(
        #     ec.presence_of_element_located(
        #         (By.CSS_SELECTOR, f'div[data-id="{backtrack}"] .chat-user-avatar')
        #     )
        # ) 
            
    
    #print(postcontent.text)
    #print(chatmessage.text)
    command = getcommand(postcontent) if not chatpm else pmcommand(postcontent)
    print(user)
    print(command)
    print(command)
    if (command == ""):
        response = random.randint(0, 3)
        x = random.randint(1, 100000)
        defaultresponse(response, chatpm)
    else:  #--------------------------------------------------------
        # print(command)
        command = command.split()
        response = random.randint(0, 3)

        x = random.randint(1, 100000)
        if command[0] == "say" and len(command) >= 2:
            del command[0]
            parrot = ' '.join(command)
            if chatpm:
                topic_content.send_keys(f"**[AUTOMATED]** \n\n {parrot}")
                topic_content.send_keys(Keys.ENTER)
                topic_content.send_keys(Keys.ENTER)
                topic_content.send_keys(Keys.ENTER)
            else:
                topic_content.send_keys(
                    f"**[AUTOMATED]** \n{parrot}<font size={x}>")

        elif command[0] == "display" and command[1] == "help":
            if chatpm:
                topic_content.send_keys(
                    f"**[AUTOMATED]** \n\nI currently know how to do the following things:"
                )
                topic_content.send_keys(Keys.ENTER)
                topic_content.send_keys(
                    f"`@bot ai stuff here`: Outputs a Gemini 1.5-Flash response with the prompt of everything after the `ai`. \n\n `@bot say hello world`: \n parrots everything after the `say`.  \n\n`@bot xkcd`\n: Generates a random [xkcd](https://xkcd.com) comic. \n\nMore coming soon! \n\n For more information, refer to [this link](https://x-camp.discourse.group/t/introducing-bot/10552?u=ivan_zong).\n"
                )

            else:
                topic_content.send_keys(
                    f"**[AUTOMATED]** \n\nI currently know how to do the following things:\n\n`@bot ai stuff here`\n> Outputs a Gemini 2.0-Flash-Experimental response with the prompt of everything after the `ai`.\n\n`@bot say hello world`\n > hello world\n\n`@bot xkcd`\n> Generates a random [xkcd](https://xkcd.com) comic.\n\nMore coming soon!\n\nFor more information, refer to [this link](https://x-camp.discourse.group/t/introducing-bot/10552?u=ivan_zong).\n<font size={x}>"
                )  #-----------------------------------------------
        elif command[0] == "ai" and len(command) > 1:
            if chatpm:
                context = "You are a bot in a discourse forum chat. Please do not use non-BMP characters in your response. If the user asks for their username but it's ERROR FETCHING USER, just say that you are unable to get the username at this time. Your responses are limited to 6000 chars."
            else:
                context = "You are a bot in a discourse forum. Please do not use non-BMP characters in your response, Do not use emojis unless specially requested by the user. Also, when doing bullet points, you only need one asterisk, afterwards it is auto bullet point, so you only need to newline. To finish the bullet points, newline 2 times."
            del command[0]
            prompt = ' '.join(command)
            fullprompt = f"{context}\n\nUser talking to you:{user}\n\nUser Prompt: {prompt}"
            output = chat.send_message(fullprompt)
            goodoutput = clean(output.text)
            print(output.text)
            if not chatpm:
                topic_content.send_keys(
                    f"**[AUTOMATED]** \n{goodoutput} \n\n<font size={x}>")
            else:
                topic_content.send_keys(f"**[AUTOMATED]** \n{goodoutput} \n")
        elif command[0] == "xkcd":
            lasturl = "https://xkcd.com/info.0.json"
            lastresponse = requests.get(lasturl)
            lastdata=lastresponse.json()
            lastcomicid=lastdata["num"]
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
            if not chatpm:
                topic_content.send_keys(f"**[AUTOMATED]** \n[spoiler]![]({comicurl})[/spoiler]\n*source: {xkcdlink}*\n\n**WARNING: SOME XKCD COMICS MAY NOT BE APPROPRIATE FOR ALL AUDIENCES. PLEASE VIEW THE ABOVE AT YOUR OWN RISK!** \n<font size={x}>")
            else:
                topic_content.send_keys(f"**[AUTOMATED]** \n[spoiler]![]({comicurl})[/spoiler]\n\n*source: {xkcdlink}*\n \n")
                topic_content.send_keys(Keys.ENTER)
                topic_content.send_keys(
                    f"**WARNING: SOME XKCD COMICS MAY NOT BE APPROPRIATE FOR ALL AUDIENCES. PLEASE VIEW THE ABOVE AT YOUR OWN RISK!**"
                )
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
        # topic_content.send_keys(Keys.ENTER)
        # time.sleep(0.02)
        # topic_content.send_keys(Keys.ENTER)
        # time.sleep(0.02)
        # topic_content.send_keys(Keys.ENTER)
        # time.sleep(0.02)
        # topic_content.send_keys(Keys.ENTER)
        # time.sleep(0.02)

    time.sleep(0.02)
    browser.refresh()
    browser.get('https://x-camp.discourse.group/')
