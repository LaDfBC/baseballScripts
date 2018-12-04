import requests
import json
import praw

#If the timer runs out, just make another call to this function.
# Gets A reddit instance the old-fashioned way.  Returns an access token
def getOauthToken(reddit_username, reddit_password, app_username, app_password):
    #Fetches ALL scopes.  Any call can be made with this variant
    r = requests.post(
        'https://www.reddit.com/api/v1/access_token'
        '?grant_type=password'
        '&username=' + reddit_username +
        '&password=' + reddit_password +
        '&redirect_uri=http://127.0.0.1:65370/reddit_callback',
        headers = {'User-agent': 'MLNStatsv0.1'},
        auth=(app_username, app_password))

    #Currently just returning the access token.
    return json.loads(r.content)['access_token']

# Gets a Reddit instance via PRAW, which is a nice wrapper over Reddit!
def getPrawInstance(app_username, app_password):
    reddit = praw.Reddit(client_id = app_username,
                         client_secret = app_password,
                         user_agent = 'MLNStatsv0.1')
    return reddit