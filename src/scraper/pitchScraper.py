import praw
from src.security import redditClient
from lxml.html import parse

# TODO: This absolutely needs to be refactored into a class, but I suck.  Please don't judge me.

# Uses the PRAW instance of Reddit
def sync_all_posts(reddit):
    posts = reddit.subreddit("BaseballbytheNumbers").hot(limit = 25)

    for post in posts:
        if post.link_flair_text == None:
            continue

        pitches = get_pitches(post)


def sync_posts_since(time):
    return None

# Hoo boy, this is the nasty function
def get_pitches(post):
    if post.link_flair_text == 'Exhibition Game' or post.link_flair_text[-8:] == 'Game Day':
        # We're returning this sucker.  It has every pitch in the game (hopefully!)
        pitches = []

        # This is a game thread - we can start trying to pull pitches!
        pitchers = __fetch_pitchers__(post)

        # Start pulling pitches and adding them to the list
        for comment in post.comments:
            if len(comment.replies) > 0:
                for first_reply in comment.replies:
                    if len(first_reply.replies) > 0:
                        # Likely a swing reply - try to find the pitch
                        reply = first_reply.replies[0]
                        pitch_reply = reply.body  # Where the pitch is displayed
                        pitch_index = __find_pitch_text__(pitch_reply)
                        end_of_pitch_line_index = pitch_reply.find("\n", pitch_index)

                        if pitch_index == -1:
                            continue
                        # TODO: GET PITCHER CORRECTLY
                        # Things we care about - pitch number, date, and pitcher (fetched above)
                        pitch_number = int(pitch_reply[pitch_index + 6:end_of_pitch_line_index].strip())
                        date = reply.created
                        pitch_data = {"number":pitch_number, "date":date, "pitcher":"TODO"}

                        pitches.append(pitch_data)
        return pitches
    else:
        return []

def __fetch_pitchers__(post):
    text = post.selftext

    teams = __fetch_teams__(post)

    pitchers_index = text.find("Pitchers") + 8

    while text.find("[", pitchers_index) != -1:
        pitcher_open_index = text.find("[", pitchers_index)
        pitcher_close_index = text.find("]", pitcher_open_index)
        pitcher_name = text[pitcher_open_index + 1 : pitcher_close_index]

    return None

def __fetch_teams__(post):
    text = parse(post.selftext_html)

    return None


# Finds the index of the line containing the pitch number
def __find_pitch_text__(comment_text):
    index = comment_text.find("Pitch:")
    if index == -1:
        index = comment_text.find("pitch:")
    return index