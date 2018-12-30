from src.fantasy.genericRowFetcher import fetchRowsFromSheetAfterRowNumber
from src.reader.googleSheetsUtil import get_spreadsheet_service, get_gspread_service
from src.spreadsheet.row_organizer import RESULT, RUNS_SCORED
import gspread

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
    "IP":"",
    "R":"",
    "K":"",
    "BB":"",
    "H":"",
    "GIDP":"",
    "IDP":"",
    "DP":"",
    "CGSO":""
}

EXCLUDED_TITLES = ['Schedule', 'Draft Order', 'Draft Picks', 'Draft Class']

def write_updates(pitcher_dict, batter_dict, spreadsheet_id):
    gc = get_gspread_service()
    overall_sheet = gc.open_by_key(spreadsheet_id)
    spreadsheets = get_spreadsheet_service(write_enabled=True)

    sheet_names = __get_all_sheet_names__(spreadsheet_id, spreadsheets)
    for sheet in sheet_names:
        # Batters
        try:
            value_list = spreadsheets.values().get(spreadsheetId=spreadsheet_id, range = sheet + '!B5:B14', majorDimension="COLUMNS").execute()['values']
        except:
            print("Empty Sheet! The sheet that exploded was " + sheet)
            continue
        batters = value_list[0]
        row_number = 5
        #TODO: STEALING, PITCHING (HITS, ER, BB) RUNS
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

                    # Updates RBI
                    if current_at_bat[RUNS_SCORED] != 0:
                        rbi_cell = batter_cells["RBI"] + str(row_number)
                        __update_cell__(rbi_cell, worksheet, increment_by=current_at_bat[RUNS_SCORED])

            # Proceed to next batter
            row_number += 1

        # PITCHER UPDATES
        row_number = 18
        pitchers = spreadsheets.values().get(spreadsheetId=spreadsheet_id, range = sheet + '!B18:B20', majorDimension="COLUMNS").execute()['values']
        for pitcher in pitchers:
            if pitcher != '':
                pitches_thrown = pitcher_dict[pitcher]
                for current_pitch_thrown in pitches_thrown:
                    result = current_pitch_thrown[RESULT]
                    if result in ['GO', 'PO', 'FO', 'K', 'SO', 'GIDP', 'DP']:
                        # Updates IP <SINGLE OUTS>
                        if result in ['GO', 'PO', 'FO', 'K', 'SO']:
                            ip_cell = pitcher_cells['IP'] + str(row_number)
                            __update_cell__(ip_cell, worksheet, increment_by=0.1)

                        # Updates IP <DOUBLE OUTS> and Double Plays
                        if result in ['GIDP', 'DP']:
                            ip_cell = pitcher_cells['IP'] + str(row_number)
                            __update_cell__(ip_cell, worksheet, increment_by=0.2)

                            dp_cell = pitcher_cells['DP'] + str(row_number)
                            __update_cell__(dp_cell, worksheet)

            row_number += 1
        # TODO: Update

    return

def __update_cell__(cell_number, worksheet, increment_by=1.0):
    current_pa = worksheet.acell(cell_number).value

    if current_pa == '':
        current_pa = 0
    worksheet.update_acell(cell_number, float(current_pa) + increment_by)

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
    pitcher_dict, player_dict = fetchRowsFromSheetAfterRowNumber(row_number=261)
    write_updates(pitcher_dict, player_dict, "126gVroUUx-erQEnKwq9lUjUPkI2WK4DxeJr2twtRre4")
