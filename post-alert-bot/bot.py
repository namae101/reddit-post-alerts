import os
import asyncio
import discord
import psycopg2
import praw
import time
from dotenv import load_dotenv

load_dotenv()

# DICORD CHANNEL ID
channelid = int(os.environ['DISCORD_CHANNEL'])
subsString = os.environ["SUBREDDITS"]
keywordsString = os.environ["KEYWORDS"]
username = os.environ['REDDIT_USERNAME']
password = os.environ['PASSWORD']
client_id = os.environ['REDDIT_ID']
client_secret = os.environ['SECRET']
user_agent = os.environ['AGENT']
token = os.environ['BOT_TOKEN']
DATABASE_URL = os.environ['DATABASE_URL']
interval = int(os.environ['INTERVAL']) * 60

client = discord.Client()


def ScrapePosts(sub, keywords):
    posts = []
    try:
        print(sub)
        reddit = praw.Reddit(client_id=client_id, client_secret=client_secret,
                             password=password, username=username, user_agent=user_agent)
        subreddit = reddit.subreddit(sub)
        # checks for any new post
        for submission in subreddit.new(limit=10):
            for keyword in keywords:
                if submission.title.lower().find(keyword) != -1 or submission.selftext.lower().find(keyword) != -1:
                    posts.append(submission)
                    print("Match for" + keyword + ": " + submission.title)
                    break
        time.sleep(2)
    except Exception as err:
        print(f'error = {err}')
        time.sleep(2)
    return posts


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    channel = client.get_channel(channelid)
    # await client.wait_until_ready()
    keywords = [keywordsString.split(",")]
    subs = subsString.split(",")
    print(keywords)
    print(subs)
    while True:
        conn = psycopg2.connect(DATABASE_URL)
        # Creating a cursor (a DB cursor is an abstraction, meant for data set traversal)
        cur = conn.cursor()
        for i in range(len(subs)):
            sub = subs[i]
            posts = ScrapePosts(sub, keywords[0])
            for p in posts:
                # Executing your PostgreSQL query
                cur.execute("SELECT EXISTS (SELECT 1 FROM reddit_post WHERE post_id = '" + str(p.id) + "');")
                post_id = cur.fetchone()[0]
                if post_id == False:
                    cur.execute("INSERT INTO reddit_post (post_id) VALUES ('" + p.id + "');")
                    # In order to make the changes to the database permanent, we now commit our changes
                    conn.commit()
                    await channel.send("[" + sub + "] \n **" + p.title + "** \n " + "https://reddit.com/"+p.permalink)
        cur.close()
        conn.close()
        await asyncio.sleep(interval)


client.run(token)
