import time
from collections import defaultdict

from gspread.exceptions import APIError
from src.reader.googleSheetsUtil import get_spreadsheet_service, get_gspread_service
from src.spreadsheet.row_organizer import get_row_as_dict, PITCHER, BATTER, RUNNER, PLAY_TYPE

GM_SPREADSHEET_SHEET_NAME = "Sheet1"
GM_SPREADSHEET_ID = "1nKl_twz731zTZ52OHn-N9ZlpAFAAR2UHK-LCg7Dyfhg"

OVERALL_SPREADSHEET_ID = '1vR8T-nZwJFYj8yKDwt0999FHzfZEEfFArZ2m1OsxPx8'

ENORMOUS_SIZE = "10000"
ENORMOUS_INT = int(ENORMOUS_SIZE)

WINNING_PITCHER = 'WP'
LOSING_PITCHER = 'LP'
SAVE_PITCHER = 'SV'

'''
Fetches ALL rows from the given spreadsheet id AFTER the given row number, defaulting to all rows.
'''
def fetchRowsFromSheetAfterRowNumber(spreadsheet_id=GM_SPREADSHEET_ID, row_number=0):
    row_number = int(row_number)
    spreadsheets = get_spreadsheet_service()

    player_to_outcome_dict = defaultdict(list)
    player_to_steal_dict = defaultdict(list)
    pitcher_to_outcome_dict = defaultdict(list)
    pitcher_to_steal_dict = defaultdict(list)

    current_row = row_number

    retry_limit = 3
    while current_row < ENORMOUS_INT:
        try:
            # TODO: Loop over this call and make it again if more than 30 rows are fetched!
            result = spreadsheets.values().get(spreadsheetId=spreadsheet_id, range=str(current_row + 1) + ":" + str(current_row + 1)).execute()
            values = result.get('values')

            if values == None:
                return pitcher_to_outcome_dict, player_to_outcome_dict, player_to_steal_dict, pitcher_to_steal_dict, current_row
            for value in values:
                mapped_row = get_row_as_dict(value, is_list=True)

                # Add to Pitcher Map
                if mapped_row[PITCHER] is not None and mapped_row[PLAY_TYPE].lower() != 'steal':
                    pitcher_to_outcome_dict[mapped_row[PITCHER]].append(mapped_row)

                # Add to Batter Map
                if mapped_row[BATTER] is not None and mapped_row[PLAY_TYPE].lower() != 'steal':
                    player_to_outcome_dict[mapped_row[BATTER]].append(mapped_row)

                if mapped_row[PLAY_TYPE].lower() == 'steal':
                    player_to_steal_dict[mapped_row[RUNNER]].append(mapped_row)
                    pitcher_to_steal_dict[mapped_row[PITCHER]].append(mapped_row)

            current_row += 1
        except:
            print("Exceeded read count on dict mapping....sleeping and retrying!")
            retry_limit -= 1
            time.sleep(100)

    return pitcher_to_outcome_dict, player_to_outcome_dict, player_to_steal_dict, pitcher_to_steal_dict, current_row

def fetchGameResults(session_number):
    gc = get_gspread_service()
    pitchers_dict = defaultdict(list)

    done = False
    while not done:
        try:
            overall_sheet = gc.open_by_key(OVERALL_SPREADSHEET_ID)
            worksheet = overall_sheet.worksheet('Games Log')
            done = True
        except APIError:
            print("Failed when fetching worksheet for game log...")

    if worksheet == None:
        raise ValueError('Missing sheet! What in the world?!')
    for row_number in range(3, 171):
        done = False
        while not done:
            try:
                cell_value = worksheet.acell('B' + str(row_number)).value
                done = True
            except:
                print ("Failed when fetching cell value")

        if cell_value == str(session_number):
            for current_game in range(row_number + 2, row_number + 9):
                done = False
                while not done:
                    try:
                        if worksheet.acell('H' + str(current_game)).value == 'FINAL':
                            winning_pitcher = worksheet.acell('K' + str(current_game)).value
                            losing_pitcher = worksheet.acell('L' + str(current_game)).value
                            saving_pitcher  = worksheet.acell('M' + str(current_game)).value

                            pitchers_dict[WINNING_PITCHER].append(winning_pitcher)
                            pitchers_dict[LOSING_PITCHER].append(losing_pitcher)
                            if saving_pitcher != '':
                                pitchers_dict[SAVE_PITCHER].append(saving_pitcher)
                        done = True
                    except APIError:
                        print('Failed to fetch pitchers!')

            return pitchers_dict
