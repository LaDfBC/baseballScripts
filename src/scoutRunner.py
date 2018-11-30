import sys
from src.security import redditOauth2Client

#Program Arg 1 is the Client Id and Program Arg 2 is the Client Secret.
# You need to provide 1337 HAX to get this information.  Or ask nicely if you're a member of MLN

def run():
    client_id = sys.argv[1]
    client_secret = sys.argv[2]

    reddit = redditOauth2Client.getPrawInstance(client_id, client_secret)

    #TODO: Actually pull and analyze data

run()