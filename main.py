import time
import random
import os
import re
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
model = genai.GenerativeModel('gemini-1.5-flash')
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
    index = thestring.find('@bot')
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


def post(browser, content, lastpost):
    try:
        reply = WebDriverWait(browser, 10).until(
            ec.element_to_be_clickable(
                (By.CSS_SELECTOR,
                 'button.btn.btn-icon-text.btn-primary.create')))
        browser.execute_script("arguments[0].scrollIntoView();", reply)
        reply.click()
    except TimeoutException:
        browser.refresh()
        reply = WebDriverWait(browser, 10).until(
            ec.element_to_be_clickable(
                (By.CSS_SELECTOR,
                 'button.btn.btn-icon-text.btn-primary.create')))
        reply.click()

    topic_content = WebDriverWait(browser, 10).until(
        ec.presence_of_element_located((
            By.CSS_SELECTOR,
            "textarea[aria-label='Type here. Use Markdown, BBCode, or HTML to format. Drag or paste images.']"
        )))
    x = int(lastpost.read()) + 1
    topic_content.send_keys(f"**[AUTOMATED]** \n{content}<font size={x}>")
    with open("lastpost.txt", "w") as lastpost:
        lastpost.write(str(x))
    reply_button = WebDriverWait(browser, 10).until(
        ec.element_to_be_clickable((
            By.CSS_SELECTOR,
            "button.btn.btn-icon-text.btn-primary.create[title='Or press Ctrl+Enter']"
        )))
    reply_button.click()


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
    lastpost = open("lastpost.txt", "r")
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
    thelink = ""
    time.sleep(1)
    while not elementfound:
        try:
            selectmention = WebDriverWait(browser, 5).until(
                ec.element_to_be_clickable(
                    (By.CSS_SELECTOR, "li.notification.unread.mentioned a")))
            elementfound = True
            thelink = selectmention.get_attribute("href")
            selectmention.click()
            break
        except stalerr:
            print("StaleElementReferenceException encountered. Retrying...")
        except TimeoutException:
            print("Try again")
            browser.refresh()
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
    print(thelink)
    postnum = getpost(thelink)
    postcontent = WebDriverWait(browser, 10).until(
        ec.presence_of_element_located((By.ID, f"post_{postnum}")))
    command = getcommand(postcontent)

    if (command == ""):
        response = random.randint(0, 3)
        x = int(lastpost.read()) + 1
        with open("lastpost.txt", "w") as lastpost:
            if response == 0:
                topic_content.send_keys(
                    f"**[AUTOMATED]**\n Hi!\n[details=\"tip\"] To find out what I can do, say `@bot display help` .[/details] \n<font size={x}>"
                )
            elif response == 1:
                topic_content.send_keys(
                    f"**[AUTOMATED]**\n Hello!\n[details=\"tip\"] To find out what I can do, say `@bot display help` .[/details] \n<font size={x}>"
                )
            elif response == 2:
                topic_content.send_keys(
                    f"**[AUTOMATED]**\n How dare you ping me\n[details=\"tip\"] To find out what I can do, say `@bot display help` .[/details] \n<font size={x}>"
                )
            elif response == 3:
                topic_content.send_keys(
                    f"**[AUTOMATED]**\n I want to take over the world!\n[details=\"tip\"] To find out what I can do, say `@bot display help` .[/details] \n<font size={x}>"
                )

            lastpost.write(str(x))
    else:
        print(command)
        command = command.split()
        response = random.randint(0, 3)
        x = int(lastpost.read()) + 1
        with open("lastpost.txt", "w") as lastpost:
            if command[0] == "say" and len(command) >= 2:
                del command[0]
                parrot = ' '.join(command)
                topic_content.send_keys(
                    f"**[AUTOMATED]** \n{parrot}<font size={x}>")
                
                    
            elif command[0] == "display" and command[1] == "help":
                topic_content.send_keys(
                    f"**[AUTOMATED]** \n\nI currently know how to do the following things:\n\n`@bot ai stuff here`\n> Outputs a Gemini 1.5-Flash response with the prompt of everything after the `ai`.\n\n`@bot say hello world`\n > hello world\n\n`@bot xkcd`\n> Generates a random [xkcd](https://xkcd.com) comic.\n\nMore coming soon!\n\nFor more information, refer to [this link](https://x-camp.discourse.group/t/introducing-bot/10552?u=ivan_zong).\n<font size={x}>"
                )
            elif command[0] == "ai" and len(command) > 1:
                context = "You are a bot in a discourse forum. Please do not use non-BMP characters in your response, Do not use emojis unless specially requested by the user. You can also use LaTeX if and only if needed. To use LaTeX, just put the command between two dollar signs. For example, $\texttt{hello}$. Also, when doing bullet points, you only need one asterisk for the whole thing. After you're done with asterisks just newline 4 times."
                del command[0]
                prompt = ' '.join(command)
                fullprompt = f"{context}\n\nUser Prompt: {prompt}"
                output = chat.send_message(fullprompt)
                goodoutput = clean(output.text)
                print(output.text)
                topic_content.send_keys(
                    f"**[AUTOMATED]** \n{goodoutput} \n\n<font size={x}>")
            elif command[0] == "xkcd":
                rand = random.randint(1, 2996)
                browser.execute_script("window.open('');")
                browser.switch_to.window(browser.window_handles[1])
                xkcdlink = 'https://xkcd.com/' + str(rand)
                browser.get(xkcdlink)
                thingy = WebDriverWait(browser, 10).until(
                    ec.presence_of_element_located(
                        (By.CSS_SELECTOR,
                         "img[style='image-orientation:none']")))
                srce = thingy.get_attribute("src")
                print(srce)
                src2 = str(srce)
                browser.close()
                browser.switch_to.window(browser.window_handles[0])
                topic_content.send_keys(
                    f"**[AUTOMATED]** \n[spoiler]![]({src2})[/spoiler]\n*source: {xkcdlink}*\n\n**WARNING: SOME XKCD COMICS MAY NOT BE APPROPRIATE FOR ALL AUDIENCES. PLEASE VIEW THE ABOVE AT YOUR OWN RISK!** \n<font size={x}>"
                )
            elif response == 0:
                topic_content.send_keys(
                    f"**[AUTOMATED]**\n Hi!\n[details=\"tip\"] To find out what I can do, say `@bot display help` .[/details] \n<font size={x}>"
                )
            elif response == 1:
                topic_content.send_keys(
                    f"**[AUTOMATED]**\n Hello!\n[details=\"tip\"] To find out what I can do, say `@bot display help` .[/details] \n<font size={x}>"
                )
            elif response == 2:
                topic_content.send_keys(
                    f"**[AUTOMATED]**\n How dare you ping me\n[details=\"tip\"] To find out what I can do, say `@bot display help` .[/details] \n<font size={x}>"
                )
            elif response == 3:
                topic_content.send_keys(
                    f"**[AUTOMATED]**\n I want to take over the world!\n[details=\"tip\"] To find out what I can do, say `@bot display help` .[/details] \n<font size={x}>"
                )
            lastpost.write(str(x))

    reply_button = WebDriverWait(browser, 10).until(
        ec.element_to_be_clickable((
            By.CSS_SELECTOR,
            "button.btn.btn-icon-text.btn-primary.create[title='Or press Ctrl+Enter']"
        )))
    reply_button.click()

    time.sleep(2)
    browser.refresh()
    browser.get('https://x-camp.discourse.group/')
