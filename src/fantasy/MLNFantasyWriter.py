import math
import sys
import time

from googleapiclient.errors import HttpError
from gspread.exceptions import APIError

from src.fantasy.genericRowFetcher import fetchRowsFromSheetAfterRowNumber
from src.reader.googleSheetsUtil import get_spreadsheet_service, get_gspread_service
from src.spreadsheet.row_organizer import RESULT, RUNS_SCORED

batter_cells = {
    "PA":"H",
    "AB":"I",
    "R":"J",
    "H":"K",
    "1B":"L",
    "2B":"M",
    "3B":"N",
    "HR":"O",
    "RBI":"P",
    "BB":"Q",
    "K":"R",
    "SO":"R",
    "SB":"S",
    "CS":"T",
    "GIDP":"U",
    "DP":"U"
}

pitcher_cells = {
    "IP":"H",
    'H': "I",
    "K": "J",
    "ER":"K",
    "BB":"L",
    "SO":"M",
    "GIDP":"Q",
    "IDP":"Q",
    "DP":"Q",
    "CGSO":"R"
}

EXCLUDED_TITLES = ['Schedule', 'Draft Order', 'Draft Picks', 'Draft Class', 'WK1 H2H Matchups']

def write_updates(pitcher_dict, batter_dict, player_steal_dict, spreadsheet_id):
    gc = get_gspread_service()
    overall_sheet = gc.open_by_key(spreadsheet_id)
    spreadsheets = get_spreadsheet_service(write_enabled=True)

    retry_limit = 3
    while retry_limit > 0:
        try:
            sheet_names = __get_all_sheet_names__(spreadsheet_id, spreadsheets)
        except:
            print("Failed getting sheet names! Retrying...")
            retry_limit -= 1
            time.sleep(60)
    for sheet in sheet_names:
        # Batters
        try:
            value_list = spreadsheets.values().get(spreadsheetId=spreadsheet_id, range = sheet + '!B5:B14', majorDimension="COLUMNS").execute()['values']
        except HttpError:
            print("Failed fetching")
            time.sleep(60)
            value_list = spreadsheets.values().get(spreadsheetId=spreadsheet_id, range = sheet + '!B5:B14', majorDimension="COLUMNS").execute()['values']
        except:
            print("Empty Sheet! The sheet that exploded was " + sheet)
            continue
        batters = value_list[0]
        row_number = 5
        worksheet = overall_sheet.worksheet(sheet)

        # UPDATE BATTERS
        for batter in batters:
            if batter != "":
                at_bats = batter_dict[batter]
                for current_at_bat in at_bats:
                    # Simply updates the number of plate appearances
                    pa_cell = batter_cells['PA'] + str(row_number)
                    __update_cell__(pa_cell, worksheet)

                    # Updates the result row of the current AB
                    if current_at_bat[RESULT] in batter_cells:
                        result_cell = batter_cells[current_at_bat[RESULT]] + str(row_number)
                        __update_cell__(result_cell, worksheet)

                        # Updates the "Hits" column
                        if current_at_bat[RESULT] in ['1B', '2B', '3B', 'HR', 'IF1B']:
                            hit_cell = batter_cells['H'] + str(row_number)
                            __update_cell__(hit_cell, worksheet)

                    # Updates RBI
                    if current_at_bat[RUNS_SCORED] != 0 and current_at_bat[RUNS_SCORED] != '':
                        rbi_cell = batter_cells["RBI"] + str(row_number)
                        __update_cell__(rbi_cell, worksheet, increment_by=float(current_at_bat[RUNS_SCORED]))

                    # Updates AB
                    if current_at_bat[RESULT] not in ['BB', 'IBB']:
                        ab_cell = batter_cells['AB'] + str(row_number)
                        __update_cell__(ab_cell, worksheet)

                # Updates Steals
                steals = player_steal_dict[batter]
                for current_steal in steals:
                    if current_steal[RESULT] == 'CS':
                        steal_cell = batter_cells['CS'] + str(row_number)
                        __update_cell__(steal_cell, worksheet)
                    elif current_steal[RESULT] == 'SB':
                        steal_cell = batter_cells['SB'] + str(row_number)
                        __update_cell__(steal_cell, worksheet)
                    else:
                        raise AttributeError("Unrecognized steal result: " + current_steal[RESULT])

            # Proceed to next batter
            row_number += 1

        # PITCHER UPDATES
        row_number = 18
        try:
            pitcher_list = spreadsheets.values().get(spreadsheetId=spreadsheet_id, range = sheet + '!B18:B20', majorDimension="COLUMNS").execute()['values']
        except HttpError:
            print("Failed during pitch fetching... Retrying!")
            time.sleep(60)
            pitcher_list = spreadsheets.values().get(spreadsheetId=spreadsheet_id, range = sheet + '!B18:B20', majorDimension="COLUMNS").execute()['values']
        except:
            continue
        pitchers = pitcher_list[0]
        for pitcher in pitchers:
            if pitcher != '':
                pitches_thrown = pitcher_dict[pitcher]
                for current_pitch_thrown in pitches_thrown:
                    result = current_pitch_thrown[RESULT]
                    if result in ['GO', 'PO', 'FO', 'K', 'SO', 'GIDP', 'DP', 'FC']:
                        # Updates IP <SINGLE OUTS>
                        if result in ['GO', 'PO', 'FO', 'K', 'SO', 'FC']:
                            ip_cell = pitcher_cells['IP'] + str(row_number)
                            __update_cell__(ip_cell, worksheet, increment_by=0.1)

                            if result in ['K', 'SO']:
                                strikeout_cell = pitcher_cells['K'] + str(row_number)
                                __update_cell__(strikeout_cell, worksheet)

                        # Updates IP <DOUBLE OUTS> and Double Plays
                        if result in ['GIDP', 'DP']:
                            ip_cell = pitcher_cells['IP'] + str(row_number)
                            __update_cell__(ip_cell, worksheet, increment_by=0.2)

                            dp_cell = pitcher_cells['DP'] + str(row_number)
                            __update_cell__(dp_cell, worksheet)

                    # Updates All Hits
                    if result in ['1B', '2B', '3B', 'HR', 'IF1B']:
                        hit_cell = pitcher_cells['H'] + str(row_number)
                        __update_cell__(hit_cell, worksheet)

                    # Updates Walks
                    if result in ['BB', 'IBB']:
                        walk_cell = pitcher_cells['BB'] + str(row_number)
                        __update_cell__(walk_cell, worksheet)

                    # Updates Earned Runs (ER)
                    if current_pitch_thrown[RUNS_SCORED] != '' and current_pitch_thrown is not None:
                        er_cell = pitcher_cells['ER'] + str(row_number)
                        __update_cell__(er_cell, worksheet, increment_by=int(current_pitch_thrown[RUNS_SCORED]))

            row_number += 1
    return

def __update_cell__(cell_number, worksheet, increment_by=1.0):
    retry_limit = 3
    while retry_limit > 0:
        try:
            current_pa = worksheet.acell(cell_number).value

            if current_pa == '':
                current_pa = 0

            if increment_by < 0.9 and (0.3 - (math.modf(float(current_pa))[0] + float(increment_by))) < 0.000001:
                increment_by += 0.7
            worksheet.update_acell(cell_number, str(float(current_pa) + increment_by))
            return
        except APIError:
            print("Exceeded read count....sleeping and retrying!")
            retry_limit -= 1
            time.sleep(60)


'''
Fetches all sheet names on the given spreadsheet.  Ignores non-player ones as defined by the globals in this file.
'''
def __get_all_sheet_names__(spreadsheet_id, spreadsheet_service):
    sheet_metadata = spreadsheet_service.get(spreadsheetId=spreadsheet_id).execute()
    sheets = sheet_metadata.get('sheets', '')

    titles = []
    for sheet in sheets:
        title = sheet['properties']['title']
        if title not in EXCLUDED_TITLES:
            titles.append(title)

    return titles

if __name__ == '__main__':
    row_in = 781
    spreadsheet_in = '1XnREuK1ZyCJgdRSe9eBFMkAVslVqyWS7ZHF39qvrznQ,1yHHFBNSrVSM-sdrsHoSKxoWsaZvAWTldD3QJ7A6GldA,17XC6z21vnRT9R35N19eoC3JYTp-ATH3wqJNtuCaS8so'
    if len(sys.argv) == 3:
        row_in = sys.argv[1]
        spreadsheet_in = sys.argv[2]

    spreadsheet_list = spreadsheet_in.split(',')
    while 1:
        pitcher_dict, player_dict, player_steal_dict, row_in = fetchRowsFromSheetAfterRowNumber(row_number=row_in)
        for spreadsheet_id in spreadsheet_list:
            print("Updating " + spreadsheet_id)
            write_updates(pitcher_dict, player_dict, player_steal_dict, spreadsheet_id)
        time.sleep(60)
