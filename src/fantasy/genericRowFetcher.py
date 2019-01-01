import sys
from collections import defaultdict

from src.reader.googleSheetsUtil import get_spreadsheet_service
from src.spreadsheet.row_organizer import get_row_as_dict, PITCHER, BATTER, RUNNER, PLAY_TYPE

GM_SPREADSHEET_SHEET_NAME = "Sheet1"
GM_SPREADSHEET_ID = "1nKl_twz731zTZ52OHn-N9ZlpAFAAR2UHK-LCg7Dyfhg"
ENORMOUS_SIZE = "1000000"

'''
Fetches ALL rows from the given spreadsheet id AFTER the given row number, defaulting to all rows.
'''
def fetchRowsFromSheetAfterRowNumber(spreadsheet_id=GM_SPREADSHEET_ID, row_number=0):
    spreadsheets = get_spreadsheet_service()

    # TODO: Loop over this call and make it again if more than 30 rows are fetched!
    result = spreadsheets.values().get(spreadsheetId=spreadsheet_id, range=str(row_number + 1) + ":" + ENORMOUS_SIZE).execute()
    values = result.get('values')

    player_to_outcome_dict = defaultdict(list)
    player_to_steal_dict = defaultdict(list)
    pitcher_to_outcome_dict = defaultdict(list)
    pitcher_to_steal_dict = defaultdict(list)
    for value in values:
        mapped_row = get_row_as_dict(value, is_list=True)

        # Add to Pitcher Map
        if mapped_row[PITCHER] is not None:
            pitcher_to_outcome_dict[mapped_row[PITCHER]].append(mapped_row)

        # Add to Batter Map
        if mapped_row[BATTER] is not None:
            player_to_outcome_dict[mapped_row[BATTER]].append(mapped_row)

        if mapped_row[PLAY_TYPE].lower() == 'steal':
            player_to_steal_dict[mapped_row[RUNNER]].append(mapped_row)
            pitcher_to_steal_dict[mapped_row[PITCHER]].append(mapped_row)

    return pitcher_to_outcome_dict, player_to_outcome_dict, pitcher_to_steal_dict, player_to_steal_dict