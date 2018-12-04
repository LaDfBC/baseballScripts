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
        pitchers = __fetch_pitchers__(post) # TODO: Can pass in teams to avoid duplicate calls
        teams = __fetch_teams__(post)
        position_players = __fetch_position_players__(post, teams)

        team_one_pitcher_index = 0
        team_two_pitcher_index = 0
        team_one_pitcher = pitchers[teams[0]][team_one_pitcher_index]
        team_two_pitcher = pitchers[teams[1]][team_two_pitcher_index]

        # Start pulling pitches and adding them to the list
        for comment in post.comments:
            player_mentioned = get_player_from_comment(comment)

            # Player is a pitcher - this is a pitching change.  Just swap out the team pitcher
            if player_mentioned in pitchers[teams[0]] or player_mentioned in pitchers[teams[1]]:
                # TODO: Check and report an error if the list of pitchers is too short
                if player_mentioned in pitchers[teams[0]]:
                    team_one_pitcher_index = team_one_pitcher_index + 1
                    team_one_pitcher = pitchers[teams[0]][team_one_pitcher_index]
                else:
                    team_two_pitcher_index = team_two_pitcher_index + 1
                    team_two_pitcher = pitchers[teams[1]][team_two_pitcher_index]
            # Player is a position player.  This is a swing.  Do the magic.
            elif player_mentioned is not None:
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
            # Else: Do nothing
        return pitches
    else:
        return []

def __fetch_pitchers__(post):
    text = post.selftext

    teams = __fetch_teams__(post)

    # Set up the dictionary we're going to return with empty strings for the pitchers and teams
    pitchers = {}
    pitchers[teams[0]] = []
    pitchers[teams[1]] = []

    pitchers_index = text.find("PITCHERS") + 8
    #TODO: Handle case where there are an uneven number of pitchers - this currently just swaps back and forth looking for pitchers
    first_team = True
    # This tears apart the table storing pitchers and scrapes their names out
    while text.find("[", pitchers_index) != -1:
        pitcher_open_index = text.find("[", pitchers_index)
        pitcher_close_index = text.find("]", pitcher_open_index)
        pitcher_name = text[pitcher_open_index + 1 : pitcher_close_index]

        # This is the part that needs changing from the to do above, it just swaps the teams right now, leading to bad correlation
        if first_team:
            pitchers[teams[0]].append(pitcher_name)
        else:
            pitchers[teams[1]].append(pitcher_name)
        first_team = not first_team

        pitchers_index = pitcher_close_index

    return pitchers


def __fetch_position_players__(post, teams):
    text = post.selftext

    players = {}
    players[teams[0]] = []
    players[teams[1]] = []

    batters_index = text.find("BOX") + 8

    first_team = True
    # Scrapes the table of players to get each of them and assign them to a team
    while text.find("[", batters_index) != -1:
        batter_open_index = text.find("[", batters_index)
        batter_close_index = text.find("]", batter_open_index)
        batter_name = text[batter_open_index + 1 : batter_close_index]

        if first_team:
            players[teams[0]].append(batter_name)
        else:
            players[teams[1]].append(batter_name)
        first_team = not first_team

        batters_index = batter_close_index

    return players

# Fetches both team names in a game, and returns them in a 2-element list.
def __fetch_teams__(post):
    text = post.selftext
    box_index = text.find("BOX")
    hashtag_index = text.find("#", box_index)
    ending_star_index = text.find("*", hashtag_index + 6)
    team_name_one = text[hashtag_index + 6: ending_star_index]

    hashtag_index = text.find("#", ending_star_index)
    ending_star_index = text.find("*", hashtag_index + 6)
    team_name_two = text[hashtag_index + 6: ending_star_index]

    return [team_name_one, team_name_two]

def get_player_from_comment(comment):
    comment_text = comment.body
    player_open_index = comment_text.find("[")
    player_close_index = comment_text.find("]", player_open_index)
    return comment_text[player_open_index + 1 : player_close_index]

# Finds the index of the line containing the pitch number
def __find_pitch_text__(comment_text):
    index = comment_text.find("Pitch:")
    if index == -1:
        index = comment_text.find("pitch:")
    return index