from src.scraper import TeamUtil


class Post:
    def __init__(self, post):
        self.post = post
        self.__assign_teams__()  # Assigns variables self.team_name_one and self.team_name_two
        self.users_to_pitchers, self.starting_pitchers = self.fetch_pitchers()
        self.users_to_position_players = self.__fetch_position_players__()

    def fetch_pitchers(self):
        text = self.post.selftext

        # Set up the dictionary we're going to return with empty strings for the pitchers and teams
        pitchers = {self.team_name_one: {}, self.team_name_two: {}}
        starting_pitchers = []

        og_pitch_index = text.find("PITCHERS")
        if og_pitch_index == -1:
            og_pitch_index = text.find("Pitchers")

        pitchers_index = og_pitch_index + 8
        first_team = True
        starting_one = True
        starting_two = True
        # This tears apart the table storing pitchers and scrapes their names out
        while text.find("[", pitchers_index) != -1:
            triple_pipe_check = text.find("|||", pitchers_index)

            pitcher_open_index = text.find("[", pitchers_index)
            pitcher_close_index = text.find("]", pitcher_open_index)
            pitcher_name = text[pitcher_open_index + 1: pitcher_close_index]

            if triple_pipe_check != -1 and triple_pipe_check < pitcher_open_index:
                first_team = not first_team

            username_open_index = text.find("(", pitcher_close_index)
            username_close_index = text.find(")", username_open_index)
            username = text[username_open_index + 1: username_close_index].lower().replace(" ", "")

            # This is the part that needs changing from the to do above,
            #   it just swaps the teams right now, leading to bad correlation
            if first_team:
                if starting_one:
                    starting_pitchers.append(username)
                    starting_one = False
                pitchers[self.team_name_one][username] = pitcher_name
            else:
                if starting_two:
                    starting_pitchers.append(username)
                    starting_two = False
                pitchers[self.team_name_two][username] = pitcher_name
            first_team = not first_team

            pitchers_index = pitcher_close_index

        return pitchers, starting_pitchers

    def __fetch_position_players__(self):
        text = self.post.selftext

        players = {self.team_name_one: {}, self.team_name_two: {}}

        box_index = text.find("BOX")
        if box_index == -1:
            box_index = text.find("Box")
        batters_index = box_index + 8

        first_team = True
        # Scrapes the table of players to get each of them and assign them to a team
        while text.find("[", batters_index) != -1:
            # This is watching for replaced team members. Otherwise, we have issues with parsing
            triple_pipe_check = text.find("|||", batters_index)
            batter_open_index = text.find("[", batters_index)
            batter_close_index = text.find("]", batter_open_index)
            batter_name = text[batter_open_index + 1: batter_close_index]

            if triple_pipe_check != -1 and triple_pipe_check < batter_open_index:
                first_team = not first_team

            username_open_index = text.find("(", batter_close_index)
            username_close_index = text.find(")", username_open_index)
            username = text[username_open_index + 1: username_close_index].lower().replace(" ", "")

            if first_team:
                players[self.team_name_one][username] = batter_name
            else:
                players[self.team_name_two][username] = batter_name
            first_team = not first_team

            batters_index = batter_close_index

        return players

    # Hoo boy, this is the nasty function
    def get_pitches(self):
        if self.post.link_flair_text == 'Exhibition Game' or \
                self.post.link_flair_text[-8:] == 'Game Day' or \
                self.post.link_flair_text == 'Winter Training':
            # We're returning this sucker.  It has every pitch in the game (hopefully!)
            pitches = []

            team_one_pitcher = self.starting_pitchers[0]
            team_two_pitcher = self.starting_pitchers[1]

            team_one_pitcher_usernames = self.users_to_pitchers[self.team_name_one].keys()
            team_two_pitcher_usernames = self.users_to_pitchers[self.team_name_two].keys()
            team_one_batter_usernames = self.users_to_position_players[self.team_name_one].keys()
            team_two_batter_usernames = self.users_to_position_players[self.team_name_two].keys()

            # Start pulling pitches and adding them to the list
            for comment in self.post.comments:
                # Figure out which player is batting
                player_mentioned = self.__get_player_from_comment__(comment)

                # Player is a pitcher - this is a pitching change.  Just swap out the team pitcher
                if player_mentioned in team_one_pitcher_usernames or player_mentioned in team_two_pitcher_usernames:
                    if player_mentioned in team_one_pitcher_usernames:
                        team_one_pitcher = player_mentioned
                    else:
                        team_two_pitcher = player_mentioned
                # Player is a position player.  This is a swing.  Do the magic.
                elif player_mentioned is not None:
                    if player_mentioned not in team_two_batter_usernames and \
                        player_mentioned not in team_one_batter_usernames:
                        raise Exception("What the fuck is happening?")
                    if len(comment.replies) > 0:
                        for first_reply in comment.replies:
                            if len(first_reply.replies) > 0:
                                # Check to see if this is a player replacement
                                possible_replacement = self.__get_player_from_comment__(first_reply)
                                if possible_replacement is not None:
                                    if possible_replacement in team_one_batter_usernames \
                                            or possible_replacement in team_two_batter_usernames:
                                        # Ok, it is.  Let's swap them out and dig down the rabbit hole of replies
                                        player_mentioned = possible_replacement
                                        if len(first_reply.replies) > 0:
                                            first_reply = first_reply.replies[0]

                                if player_mentioned in team_one_batter_usernames:
                                    team_two_batting = False
                                elif player_mentioned in team_two_batter_usernames:
                                    team_two_batting = True
                                else:
                                    continue
                                # Likely a swing reply - try to find the pitch
                                reply = first_reply.replies[0]
                                pitch_reply = reply.body  # Where the pitch is displayed
                                pitch_index = self.__find_pitch_text__(pitch_reply)
                                end_of_pitch_line_index = pitch_reply.find("\n", pitch_index)

                                if pitch_index == -1:
                                    continue
                                # Things we care about - pitch number, date, and pitcher (fetched above)
                                pitch_number = int(pitch_reply[pitch_index + 6:end_of_pitch_line_index].strip())
                                date = reply.created

                                if team_two_batting:
                                    pitch_data = {"number": pitch_number, "date": date,
                                                  "pitcher": self.users_to_pitchers[self.team_name_one][
                                                      team_one_pitcher]}
                                else:
                                    pitch_data = {"number": pitch_number, "date": date,
                                                  "pitcher": self.users_to_pitchers[self.team_name_two][
                                                      team_two_pitcher]}

                                pitches.append(pitch_data)
                # Else: Do nothing
            return pitches
        else:
            return []

    # Fetches both team names in a game, and assigns them to class-level variables
    def __assign_teams__(self):
        text = self.post.selftext
        teams = {}

        smallest_index = 100000
        all_indexes = []
        for abbreviation in TeamUtil.get_team_abbreviation_list():
            index = text.find(abbreviation)
            if index != -1:
                teams[abbreviation] = index
                all_indexes.append(index)
                if index < smallest_index:
                    smallest_index = index

        #This is bad - I originally threw an error, but realized I could just knock it down
        if len(teams) > 2:
            teams_to_pop = []
            all_indexes = sorted(all_indexes)
            for team in teams:
                if not teams[team] == all_indexes[0] and not teams[team] == all_indexes[1]:
                    teams_to_pop.append(team)

            for team_to_pop in teams_to_pop:
                teams.pop(team_to_pop)
        elif len(teams) < 2:
            raise ValueError("Couldn't find enough teams!")

        for team in teams:
            if teams[team] == smallest_index:
                self.team_name_one = team
            else:
                self.team_name_two = team

    @staticmethod
    def __get_player_from_comment__(comment):
        comment_text = comment.body.replace(" ", "")
        player_open_index = comment_text.find("[")
        player_close_index = comment_text.find("]", player_open_index)

        if player_open_index == -1:
            return None

        username_open_index = comment_text.find("(/u", player_close_index)
        username_close_index = comment_text.find(")", username_open_index)
        return comment_text[username_open_index + 1: username_close_index].lower()

    # Finds the index of the line containing the pitch number
    @staticmethod
    def __find_pitch_text__(comment_text):
        index = comment_text.find("Pitch:")
        if index == -1:
            index = comment_text.find("pitch:")
        return index
