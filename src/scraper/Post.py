class Post:
    def __init__(self, post):
        self.post = post
        self.teams = self.__fetch_teams__()

    def fetch_pitchers(self):
        text = self.post.selftext

        # Set up the dictionary we're going to return with empty strings for the pitchers and teams
        pitchers = {}
        pitchers[self.teams[0]] = []
        pitchers[self.teams[1]] = []

        og_pitch_index = text.find("PITCHERS")
        if og_pitch_index == -1:
            og_pitch_index = text.find("Pitchers")

        pitchers_index = og_pitch_index + 8
        # TODO: Handle case where there are an uneven number of pitchers - this currently just swaps back and forth looking for pitchers
        first_team = True
        # This tears apart the table storing pitchers and scrapes their names out
        while text.find("[", pitchers_index) != -1:
            pitcher_open_index = text.find("[", pitchers_index)
            pitcher_close_index = text.find("]", pitcher_open_index)
            pitcher_name = text[pitcher_open_index + 1: pitcher_close_index]

            # This is the part that needs changing from the to do above, it just swaps the teams right now, leading to bad correlation
            if first_team:
                pitchers[self.teams[0]].append(pitcher_name)
            else:
                pitchers[self.teams[1]].append(pitcher_name)
            first_team = not first_team

            pitchers_index = pitcher_close_index

        return pitchers

    def fetch_position_players(self,):
        text = self.post.selftext

        players = {}
        players[self.teams[0]] = []
        players[self.teams[1]] = []

        box_index = text.find("BOX")
        if box_index == -1:
            box_index = text.find("Box")
        batters_index = box_index + 8

        first_team = True
        # Scrapes the table of players to get each of them and assign them to a team
        while text.find("[", batters_index) != -1:
            batter_open_index = text.find("[", batters_index)
            batter_close_index = text.find("]", batter_open_index)
            batter_name = text[batter_open_index + 1: batter_close_index]

            if first_team:
                players[self.teams[0]].append(batter_name)
            else:
                players[self.teams[1]].append(batter_name)
            first_team = not first_team

            batters_index = batter_close_index

        return players

    # Hoo boy, this is the nasty function
    def get_pitches(self):
        if self.post.link_flair_text == 'Exhibition Game' or self.post.link_flair_text[-8:] == 'Game Day' or self.post.link_flair_text == 'Winter Training':
            # We're returning this sucker.  It has every pitch in the game (hopefully!)
            pitches = []

            # This is a game thread - we can start trying to pull pitches!
            pitchers = self.fetch_pitchers()  # TODO: Can pass in teams to avoid duplicate calls
            position_players = self.fetch_position_players()

            team_one_pitcher_index = 0
            team_two_pitcher_index = 0
            team_one_pitcher = pitchers[self.teams[0]][team_one_pitcher_index]
            team_two_pitcher = pitchers[self.teams[1]][team_two_pitcher_index]

            # Start pulling pitches and adding them to the list
            for comment in self.post.comments:

                #TODO: This needs to be a function
                player_mentioned = self.__get_player_from_comment__(comment)
                player_mentioned = player_mentioned.split(" ")[-2:]
                player_mentioned = player_mentioned[0] + " " + player_mentioned[1]

                # Player is a pitcher - this is a pitching change.  Just swap out the team pitcher
                if player_mentioned in pitchers[self.teams[0]] or player_mentioned in pitchers[self.teams[1]]:
                    # TODO: Check and report an error if the list of pitchers is too short
                    if player_mentioned in pitchers[self.teams[0]]:
                        team_one_pitcher_index = team_one_pitcher_index + 1
                        team_one_pitcher = pitchers[self.teams[0]][team_one_pitcher_index]
                    else:
                        team_two_pitcher_index = team_two_pitcher_index + 1
                        team_two_pitcher = pitchers[self.teams[1]][team_two_pitcher_index]
                # Player is a position player.  This is a swing.  Do the magic.
                elif player_mentioned is not None:
                    if len(comment.replies) > 0:
                        for first_reply in comment.replies:
                            if len(first_reply.replies) > 0:
                                if player_mentioned in position_players[self.teams[0]]:
                                    team_two_batting = False
                                else:
                                    team_two_batting = True
                                # Likely a swing reply - try to find the pitch
                                reply = first_reply.replies[0]
                                pitch_reply = reply.body  # Where the pitch is displayed
                                pitch_index = self.__find_pitch_text__(pitch_reply)
                                end_of_pitch_line_index = pitch_reply.find("\n", pitch_index)

                                if pitch_index == -1:
                                    continue
                                # TODO: GET PITCHER CORRECTLY
                                # Things we care about - pitch number, date, and pitcher (fetched above)
                                pitch_number = int(pitch_reply[pitch_index + 6:end_of_pitch_line_index].strip())
                                date = reply.created

                                if team_two_batting:
                                    pitch_data = {"number": pitch_number, "date": date, "pitcher": team_one_pitcher}
                                else:
                                    pitch_data = {"number": pitch_number, "date": date, "pitcher": team_two_pitcher}

                                pitches.append(pitch_data)
                # Else: Do nothing
            return pitches
        else:
            return []

    # Fetches both team names in a game, and returns them in a 2-element list.
    def __fetch_teams__(self):
        text = self.post.selftext
        box_index = text.find("BOX")
        if box_index == -1:
            box_index = text.find("Box")
        hashtag_index = text.find("#", box_index) + 2
        ending_pipe_index = text.find("|", hashtag_index)
        team_name_one = text[hashtag_index : ending_pipe_index]

        hashtag_index = text.find("#", ending_pipe_index) + 2
        ending_pipe_index = text.find("|", hashtag_index)
        team_name_two = text[hashtag_index : ending_pipe_index]

        return [team_name_one, team_name_two]

    def __get_player_from_comment__(self, comment):
        comment_text = comment.body
        player_open_index = comment_text.find("[")
        player_close_index = comment_text.find("]", player_open_index)
        return comment_text[player_open_index + 1: player_close_index]

    # Finds the index of the line containing the pitch number
    def __find_pitch_text__(self, comment_text):
        index = comment_text.find("Pitch:")
        if index == -1:
            index = comment_text.find("pitch:")
        return index