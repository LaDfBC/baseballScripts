PLAY_NUMBER = 'play_number'
INNING = 'inning'
OUTS = 'outs'
BRC = 'brc'
PLAY_TYPE = 'play'
PITCHER = 'pitcher'
PITCH_VALUE = 'pitch_value'
BATTER = 'batter'
SWING_VALUE = 'swing_value'
CATCHER = 'catcher'
THROW_VALUE = 'throw_value'
RUNNER = 'runner'
STEAL_VALUE = 'steal_value'
RESULT = 'result'
RUNS_SCORED = 'runs_scored'
AWAY_SCORE = 'away_scored'
OBC = 'obc'
LEVERAGE = 'leverage'
HOME_WE = 'home_we'
GHOST_SCORED = 'ghost_scored'
RBI = 'rbi'
STOLEN_BASE = 'stolen'
DIFF = 'diff'
RUNS_SCORED_ON_PLAY = 'play_runs_scored'
OFF_TEAM = 'offense'
DEF_TEAM = 'defense'
GAME_NUMBER = 'game_number'

def get_row_as_dict(row, mlr=False):
    split_row = row.split(',')

    if mlr:
        return __get_mlr_row__(split_row)
    else:
        return __get_mln_row__(split_row)

def __get_mlr_row__(split_row):
    ret_dict = {}

    ret_dict[BATTER] = split_row[0]
    ret_dict[SWING_VALUE] = split_row[1]
    ret_dict[PITCHER] = split_row[2]
    ret_dict[PITCH_VALUE] = split_row[3]
    ret_dict[RESULT] = split_row[4]
    ret_dict[DIFF] = split_row[5]
    ret_dict[INNING] = split_row[6]
    ret_dict[OUTS] = split_row[7]
    ret_dict[RUNS_SCORED] = split_row[8]
    ret_dict[AWAY_SCORE] = split_row[9]
    ret_dict[OBC] = split_row[10]
    ret_dict[LEVERAGE] = split_row[11]
    ret_dict[HOME_WE] = split_row[12]
    ret_dict[RBI] = split_row[13]
    ret_dict[RUNS_SCORED_ON_PLAY] = split_row[14]

    return ret_dict

def __get_mln_row__(split_row):
    ret_dict = {}
    ret_dict[PLAY_NUMBER] = split_row[0]
    ret_dict[INNING] = split_row[1]
    ret_dict[OUTS] = split_row[2]
    ret_dict[BRC] = split_row[3]
    ret_dict[PLAY_TYPE] = split_row[4]
    ret_dict[PITCHER] = split_row[5]
    ret_dict[PITCH_VALUE] = split_row[6]
    ret_dict[BATTER] = split_row[7]
    ret_dict[SWING_VALUE] = split_row[8]
    ret_dict[CATCHER] = split_row[9]
    ret_dict[THROW_VALUE] = split_row[10]
    ret_dict[RUNNER] = split_row[11]
    ret_dict[STEAL_VALUE] = split_row[12]
    ret_dict[RESULT] = split_row[13]
    ret_dict[RUNS_SCORED] = split_row[14]
    ret_dict[GHOST_SCORED] = split_row[15]
    ret_dict[RBI] = split_row[16]
    ret_dict[STOLEN_BASE] = split_row[17]
    ret_dict[DIFF] = split_row[18]
    ret_dict[RUNS_SCORED_ON_PLAY] = split_row[19]
    ret_dict[OFF_TEAM] = split_row[20]
    ret_dict[DEF_TEAM] = split_row[21]
    ret_dict[GAME_NUMBER] = split_row[22]

    return ret_dict

