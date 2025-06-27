from selenium.webdriver.common.keys import Keys
import random
def help(chatpm, topic_content):
    x = random.randint(1, 1000000)
    if chatpm:
        topic_content.send_keys(
            "**[AUTOMATED]** \n\nI currently know how to do the following things:"
        )
        topic_content.send_keys(Keys.ENTER)
        topic_content.send_keys(Keys.ENTER)
        topic_content.send_keys(
            "`@bot ai [PROMPT]`: Outputs a Gemini 2.0-Flash Experimental response with the prompt of everything after the `ai`."
        )
        topic_content.send_keys(Keys.ENTER)
        topic_content.send_keys(
            "`@bot user [USER]`: Gives all the information of the user requested. If the user is left blank, it will give all the information of you."
        )
        topic_content.send_keys(Keys.ENTER)
        topic_content.send_keys(Keys.ENTER)
        topic_content.send_keys(
            "`@bot support` or `@bot suggest`: Creates a support ticket (a PM) to me and the user."
        )
        topic_content.send_keys(Keys.ENTER)
        topic_content.send_keys(
            "`@bot say [PARROTED TEXT]`: Parrots everything after the `say`."
        )
        topic_content.send_keys(Keys.ENTER)
        topic_content.send_keys(
            "`@bot fortune`: Gives you a random [Magic 8 Ball](https://magic-8ball.com/) answer."
        )
        topic_content.send_keys(Keys.ENTER)
        topic_content.send_keys(
            "`@bot roll [DICE]d[SIDES]` or `@bot roll [SIDES]`: Rolls the number of [DICE], each  with [SIDES] sides."
        )
        topic_content.send_keys(Keys.ENTER)
        topic_content.send_keys(
            "`@bot version` or `@bot ver` or `@bot changlog` or `@bot log`: Outputs the current version and the description of the last recorded change of me."
        )
        topic_content.send_keys(Keys.ENTER)
        topic_content.send_keys(
            "`@bot xkcd`: Generates a random [xkcd](https://xkcd.com) comic."
        )
        topic_content.send_keys(Keys.ENTER)
        topic_content.send_keys(
            "`@bot xkcd last` or `@bot xkcd latest`: Outputs the most recent [xkcd](https://xkcd.com) comic."
        )
        topic_content.send_keys(Keys.ENTER)
        topic_content.send_keys(
            "`@bot xkcd blacklist`: Outputs all of the blacklisted XKCD comic ID's."
        )
        topic_content.send_keys(Keys.ENTER)
        topic_content.send_keys(
            "`@bot xkcd blacklist comic [ID HERE]`: Blacklists the comic with the ID. Only authorized users can execute this command."
        )
        topic_content.send_keys(Keys.ENTER)
        topic_content.send_keys(
            "`@bot xkcd comic [ID HERE]`: Gives you the xkcd comic with the ID along with some info on the comic."
        )
        topic_content.send_keys(Keys.ENTER)
        topic_content.send_keys("More coming soon! ")
        topic_content.send_keys(Keys.ENTER)
        topic_content.send_keys(Keys.ENTER)
        topic_content.send_keys(
            "For more information, visit [the README github page for bot](https://github.com/LiquidPixel101/Bot/blob/main/README.md)."
        )
        topic_content.send_keys(Keys.ENTER)

    else:
        topiccontent = f"**[AUTOMATED]** \n\nI currently know how to do the following things:\n\n`@bot ai [PROMPT]`\n> Outputs a Gemini 2.0-Flash-Experimental response with the prompt of everything after the `ai`.\n\n`@bot user`\n > Gives all the information of the user requested. If the user is left blank, it will give all the information of you.\n\n`@bot support` or `@bot suggest`\n> Creates a support ticket (a PM) to me and the user.\n\n`@bot say [PARROTED TEXT]`\n > Parrots everything after the `say`.\n\n`@bot fortune`\n > Gives you a random [Magic 8 Ball](https://magic-8ball.com/) answer.\n\n`@bot roll [DICE]d[SIDES]` or `@bot roll [SIDES]`\n > Rolls the number of [DICE], each  with [SIDES] sides.\n\n`@bot about`\n> Outputs the [README](https://github.com/LiquidPixel101/Bot/blob/main/README.md). It has all the information about me!\n\n`@bot version` or `@bot ver` or `@bot changlog` or `@bot log`\n > Outputs the current version and the full changelog of me!\n\n`@bot xkcd`\n> Generates a random [xkcd](https://xkcd.com) comic.\n\n`@bot xkcd last` or `@bot xkcd latest`\n > Outputs the most recent [xkcd](https://xkcd.com) comic. \n\n `@bot xkcd blacklist` \n > Outputs all of the blacklisted XKCD comic ID's and a list of reasons of why they might have been blacklisted. \n\n`@bot xkcd blacklist comic [ID HERE]` \n > Blacklists the comic with the ID. Only authorized users can execute this command. \n\n  `@bot xkcd comic [ID HERE]` or `@bot xkcd [ID HERE]`\n > Gives you the xkcd comic with the ID along with some info on the comic.\n\n`@bot run [python/c++] [CODE]`\n > Runs the Python/C++ given. (Thanks to @<aaa>e for the massive help!) \n\nMore coming soon!\n\n\nFor more information, click [here](https://github.com/LiquidPixel101/Bot/blob/main/README.md).<font size={x}>"
