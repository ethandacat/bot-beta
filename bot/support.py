from replit import db
import time
from selenium.webdriver.common.keys import Keys
import random
from utils import *
def support(chatpm, topic_content, reqs, user, command, rawpost):
    x = random.randint(1, 10000000)
    forum_url = "https://x-camp.discourse.group"
    if chatpm:
        topic_content.send_keys("**[AUTOMATED]**")
        topic_content.send_keys(Keys.ENTER)
        topic_content.send_keys(Keys.ENTER)
        topic_content.send_keys("Creating support ticket...")
        topic_content.send_keys(Keys.ENTER)
    csrf_resp = reqs.get(f"{forum_url}/session/csrf.json")
    csrf_token = csrf_resp.json().get("csrf")
    reqs.headers.update(
        {
            "X-CSRF-Token": csrf_token,
            "Content-Type": "application/json",
        }
    )
    if chatpm:
        del command[0]
    contents = " ".join(command) if chatpm else rawpost[9:]
    if db["me"] == user:
        payload = {
            "title": f"Support Ticket #{db['support']}",
            "raw": "**[AUTOMATED]**\n" + contents + f"\n<font size={x+1}>",
            "archetype": "private_message",
            "target_recipients": f"{db['me']}",
        }
    else:
        payload = {
            "title": f"Support Ticket #{db['support']}",
            "raw": "**[AUTOMATED]**\n" + contents + f"\n<font size={x+1}>",
            "archetype": "private_message",
            "target_recipients": f"{db['me']},{user}",
        }
    response = reqs.post(f"{forum_url}/posts.json", json=payload)
    if response.status_code == 200:
        print("✅ PM sent successfully!")
        db["support"] = db["support"] + 1
        if chatpm:
            topic_content.send_keys(Keys.ENTER)
            topic_content.send_keys("✅ **Support ticket created successfully!**")
            topic_content.send_keys(Keys.ENTER)
            topic_content.send_keys(Keys.ENTER)
        else:
            topiccontent = f"**[AUTOMATED]**\n\n ✅ **Support ticket created successfully!**\n\nContents:\n```{contents}``` \n <font size={x}>"
        time.sleep(5)
        # print(response.json())
    else:
        print(f"❌ Failed to send PM. Status: {response.status_code}")
        print("Response:", response.text)
        if chatpm:
            topic_content.send_keys(Keys.ENTER)
            topic_content.send_keys("❌ **Failed to create ticket.**")
            topic_content.send_keys(Keys.ENTER)
            topic_content.send_keys(Keys.ENTER)
            topic_content.send_keys("DEBUG:")
            topic_content.send_keys(Keys.ENTER)
            topic_content.send_keys(Keys.ENTER)
            topic_content.send_keys(f"Status: {response.status_code}")
            topic_content.send_keys(Keys.ENTER)
            topic_content.send_keys(Keys.ENTER)
            topic_content.send_keys("Response:", response.text)
        else:
            topiccontent = f'**[AUTOMATED]**\n\n ❌ **Failed to create ticket.**\n[details="DEBUG"]\nStatus: {response.status_code}\nResponse: {response.text}\n[/details]\n<font size={x}>'

def user(command, reqs, chatpm, topic_content):
    x = random.randint(1, 10000000)
    username = ""
    username = user if len(command) == 1 else command[1]
    userdata = reqs.get(f"https://x-camp.discourse.group/u/{username}.json")
    if userdata.status_code != 200:
        if chatpm:
            topic_content.send_keys("**[AUTOMATED]**")
            topic_content.send_keys(Keys.ENTER)
            topic_content.send_keys(
                "There is an error with your request - perhaps that user doesn't exist?"
            )
        else:
            topiccontent = f"**[AUTOMATED]**\n\nThere is an error with your request - perhaps that user doesn't exist?<font size={x}>"
    else:
        userdata = userdata.json()
        if "https://" in userdata["user"]["avatar_template"]:
            pfp = userdata["user"]["avatar_template"].replace("{size}", "288")
        else:
            pfp = "https://sea2.discourse-cdn.com/flex020" + userdata["user"][
                "avatar_template"
            ].replace("{size}", "288")
        trustlevels = ["New User", "Basic", "Member", "Regular", "Leader"]
        id = userdata["user"]["id"]
        autom = False
        if id <= 0:
            id = "This account was created automatically when this discourse was made."
            autom = True
        displayname = userdata["user"]["name"]

        title = userdata["user"]["title"]
        if title is None or title == "":
            title = "None"
        username = userdata["user"]["username"]
        if not (
            "profile_hidden" in userdata["user"]
            and userdata["user"]["profile_hidden"] == True
        ):

            lastposted = userdata["user"]["last_posted_at"]
            if lastposted is None:
                lastposted = "This user has never posted before."
            else:
                lastposted = convertime(lastposted)
            lastseen = userdata["user"]["last_seen_at"]
            if lastseen is None:
                lastseen = "This user is either a bot or had never been online before."
            else:
                lastseen = convertime(lastseen)
            created = userdata["user"]["created_at"]
            created = convertime(created)
            banned = userdata["user"]["ignored"]
            trustlevel = userdata["user"]["trust_level"]
            ismod = userdata["user"]["moderator"]
            isadmin = userdata["user"]["admin"]
            badgecnt = userdata["user"]["badge_count"]
            readtime = formatduration(userdata["user"]["time_read"])
            timezone = userdata["user"]["timezone"]
            if "bio_raw" in userdata["user"]:
                bio = userdata["user"]["bio_raw"]
            else:
                bio = "ERROR: This user does not have a bio."
            pfviews = userdata["user"]["profile_view_count"]
            cheers = userdata["user"]["gamification_score"]
            solutions = userdata["user"]["accepted_answers"]
        if chatpm:
            topic_content.send_keys("**[AUTOMATED]**")
            topic_content.send_keys(Keys.ENTER)
            topic_content.send_keys(pfp)
            topic_content.send_keys(Keys.ENTER)
            topic_content.send_keys(f"<mark> [b] {displayname} [/b]</mark>\n\n")
            topic_content.send_keys(Keys.ENTER)
            time.sleep(0.1)
            topic_content.send_keys(Keys.ENTER)
            topic_content.send_keys(f"**Username:** {username}\n\n")
            topic_content.send_keys(Keys.ENTER)
            time.sleep(0.1)
            topic_content.send_keys(Keys.ENTER)
            topic_content.send_keys(f"**Title:** {title}")
            topic_content.send_keys(Keys.ENTER)
            time.sleep(0.1)
            topic_content.send_keys(Keys.ENTER)
            if autom == False:
                topic_content.send_keys(
                    f"**{id}{suffix(id)} person to join this forum**"
                )
            else:
                topic_content.send_keys(f"**{id}**")
            topic_content.send_keys(Keys.ENTER)
            time.sleep(0.1)
            topic_content.send_keys(Keys.ENTER)
            if (
                "profile_hidden" in userdata["user"]
                and userdata["user"]["profile_hidden"] == True
            ):
                topic_content.send_keys("This user has their profile hidden.")
                topic_content.send_keys(Keys.ENTER)
                time.sleep(0.1)
                topic_content.send_keys(Keys.ENTER)
            else:
                topic_content.send_keys(
                    f"**Trust level:** {trustlevel} ({trustlevels[trustlevel]})"
                )
                topic_content.send_keys(Keys.ENTER)
                time.sleep(0.1)
                topic_content.send_keys(Keys.ENTER)
                topic_content.send_keys(f"**Cheers:** {cheers}")
                topic_content.send_keys(Keys.ENTER)
                time.sleep(0.1)
                topic_content.send_keys(Keys.ENTER)
                topic_content.send_keys(f"**Timezone:** {timezone}")
                topic_content.send_keys(Keys.ENTER)
                time.sleep(0.1)
                topic_content.send_keys(Keys.ENTER)
                topic_content.send_keys(f"**Solutions:** {solutions}")
                topic_content.send_keys(Keys.ENTER)
                time.sleep(0.1)
                topic_content.send_keys(Keys.ENTER)
                topic_content.send_keys(f"**Badge Count:** {badgecnt}")
                topic_content.send_keys(Keys.ENTER)
                time.sleep(0.1)
                topic_content.send_keys(Keys.ENTER)
                topic_content.send_keys(f"**Read Time:** {readtime}")
                topic_content.send_keys(Keys.ENTER)
                time.sleep(0.1)
                topic_content.send_keys(Keys.ENTER)
                topic_content.send_keys(f"**Profile Views:** {pfviews}")
                topic_content.send_keys(Keys.ENTER)
                time.sleep(0.1)
                topic_content.send_keys(Keys.ENTER)
                topic_content.send_keys(f"**Last Posted:** {lastposted}")
                topic_content.send_keys(Keys.ENTER)
                time.sleep(0.1)
                topic_content.send_keys(Keys.ENTER)
                topic_content.send_keys(f"**Last Seen:** {lastseen}")
                topic_content.send_keys(Keys.ENTER)
                time.sleep(0.1)
                topic_content.send_keys(Keys.ENTER)
                topic_content.send_keys(f"**Account Created:** {created}")
                topic_content.send_keys(Keys.ENTER)
                time.sleep(0.1)
                topic_content.send_keys(Keys.ENTER)
                topic_content.send_keys(f"**Is moderator?** {ismod}")
                topic_content.send_keys(Keys.ENTER)
                time.sleep(0.1)
                topic_content.send_keys(Keys.ENTER)
                topic_content.send_keys(f"**Is admin?** {isadmin}")
                topic_content.send_keys(Keys.ENTER)
                time.sleep(0.1)
                topic_content.send_keys(Keys.ENTER)
                topic_content.send_keys("**Bio:** ")
                topic_content.send_keys(Keys.ENTER)
                time.sleep(0.1)
                topic_content.send_keys(Keys.ENTER)
                topic_content.send_keys("```")
                topic_content.send_keys(Keys.SHIFT, Keys.ENTER)
                for part in bio.split("\n"):
                    topic_content.send_keys(part)
                    topic_content.send_keys(Keys.SHIFT, Keys.ENTER)
                topic_content.send_keys("```")
                topic_content.send_keys(Keys.ENTER)
                time.sleep(0.1)
                topic_content.send_keys(Keys.ENTER)
                topic_content.send_keys(f"**Banned by @bot?** {banned}")
                topic_content.send_keys(Keys.ENTER)
                time.sleep(0.1)
                topic_content.send_keys(Keys.ENTER)
        else:
            topiccontent = f"**[AUTOMATED]**\n{pfp}\n# {displayname}\n## {username}\n\n**Title:** {title}\n"
            if autom == False:
                topiccontent += f"**{id}{suffix(id)} person to join this forum**"
            else:
                topiccontent += f"**{id}**"
            if (
                "profile_hidden" in userdata["user"]
                and userdata["user"]["profile_hidden"] == True
            ):
                topiccontent += "\n**This user has their profile hidden.**"
            else:
                topiccontent += f"\n**Trust level:** {trustlevel} ({trustlevels[trustlevel]})\n**Cheers:** {cheers}\n**Timezone:** {timezone}\n**Solutions:** {solutions}\n**Badge Count:** {badgecnt}\n**Read Time:** {readtime}\n**Profile Views:** {pfviews}\n**Last Posted:** {lastposted}\n**Last Seen:** {lastseen}\n**Account Created:** {created}\n**Is moderator?** {ismod}\n**Is admin?** {isadmin}\n**Bio:**\n```\n{bio}\n```\n**Banned by @bot?** {banned}\n<font size={x}>"
