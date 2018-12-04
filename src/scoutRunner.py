import sys
from src.security import redditClient
from src.scraper import pitchScraper

#Program Arg 1 is the Client Id and Program Arg 2 is the Client Secret.
# You need to provide 1337 HAX to get this information.  Or ask nicely if you're a member of MLN

def run():
    client_id = sys.argv[1]
    client_secret = sys.argv[2]

    reddit = redditClient.getPrawInstance(client_id, client_secret)
    pitchScraper.sync_all_posts(reddit)

run()