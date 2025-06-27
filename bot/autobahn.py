from replit import db
from ai import get
from utils import *

def get_new_posts(topicid, reqs):
    res = reqs.get(f"https://x-camp.discourse.group/t/{topicid}.json")
    data = res.json()
    posts = data["post_stream"]["posts"]

    max_post_id = max(post["id"] for post in posts)

    # get last seen post id from db or default to 0
    last_id = db.get("last_seen_post_id", {}).get(str(topicid), 0)

    # filter new posts
    new_posts = [post for post in posts if post["id"] > last_id]

    # update db
    if max_post_id > last_id:
        if "last_seen_post_id" not in db:
            db["last_seen_post_id"] = {}
        db["last_seen_post_id"][str(topicid)] = max_post_id

    return [data,new_posts]


def sbr(msg):
    msg = msg.lower()
    score = 0

    keywords = {
        "help": 3,
        "error": 3,
        "fix": 2,
        "issue": 2,
        "problem": 2,
        "explain": 2,
        "bot": 3,
        "@bot": -100,
        "?": 1,
    }

    for word, weight in keywords.items():
        if word in msg:
            score += weight

    # check question words at start
    question_words = ["how", "why", "what", "when", "where", "who", "can", "could", "would", "should"]
    if any(msg.startswith(qw) for qw in question_words):
        score += 2

    return score >= 3


def autobahn(tid, data, reqs, topicid, BOT_USERNAME):
    # data is the full topic JSON (the first element returned by get_new_posts)
    posts = data["post_stream"]["posts"]

    # get last seen post id for filtering
    last_id = db.get("last_seen_post_id", {}).get(str(tid), 0)

    # filter new posts
    new_posts = [post for post in posts if post["id"] > last_id]

    for post in new_posts:
        author = post["username"]
        content = post["cooked"]

        if author == BOT_USERNAME:
            continue

        if not sbr(content):
            continue

        #############AUTOBAHN#############

        # autobahn ai
        fullprompt = f"User talking to you:{author}\n\n {content}"
        outpoot_by_facedev = get(fullprompt)
        goodout = clean(outpoot_by_facedev) # i got lazy with var names
        topiccontent = "**[AUTOMATED]**\n"+goodout
        #############AUTOBAHN#############

        # its positn time
        print("\nPowered w/ AUTOBAHN by Ethan.")
        print(topiccontent)
        csrfres = reqs.get('https://x-camp.discourse.group/session/csrf.json')
        if csrfres.status_code != 200:
            print('CSRF error:', csrfres.status_code, csrfres.text)
            exit()
        csrftoken = csrfres.json().get('csrf')
        if not csrftoken:
            print('Missing CSRF token')
            exit()

        reqs.headers.update({
            'X-CSRF-Token': csrftoken,
            'Content-Type': 'application/json',
            'Referer': f'https://x-camp.discourse.group/t/{topicid}'
        })

        payload = {'raw': topiccontent, 'topic_id': tid}
        posturl = 'https://x-camp.discourse.group/posts'

        dastatus = reqs.post(posturl, json=payload)
        if dastatus.status_code == 200:
            print('Post successful:', dastatus.json().get('id'))
        else:
            print(f'Failed to post: {dastatus.status_code} {dastatus.text}')
            try:
                if dastatus.json().get('error_type') == 'rate_limit':
                    time.sleep(10)
                    dastatus = reqs.post(posturl, json=payload)
                    if dastatus.status_code == 200:
                        print('Post successful after retry:', dastatus.json().get('id'))
                    else:
                        print(f'Retry failed: {dastatus.status_code} {dastatus.text}')
            except Exception:
                pass


    # update last seen post id in db after processing all
    if new_posts:
        max_post_id = max(post["id"] for post in new_posts)
        if "last_seen_post_id" not in db:
            db["last_seen_post_id"] = {}
        db["last_seen_post_id"][str(tid)] = max_post_id
