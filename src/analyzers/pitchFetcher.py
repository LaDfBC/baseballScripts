from src.analyzers.distributionAnalyzer import groupValuesByRange
from src.analyzers.googleSheetsUtil import get_spreadsheet_service
from src.spreadsheet.row_organizer import PITCHER, PITCH_VALUE, GAME_NUMBER, get_row_as_dict

'''
Uses a filename on the local machine and a pitcher name to analyze to fetch all of pitches thrown by the named person
and then return them all in the order they were thrown, as well as the "Deltas" between the pitches - that is, the difference
between the values of each pitch thrown by that person.

These lists are commonly fed into the distributation analyzer stuff to produce reports about the pitches
'''
def fetchPitchesByPitcherAndLocalFile(file_name, pitcher_name):
    pitches = []
    deltas = []

    pitcher_name = pitcher_name.lower()
    previous_pitch = None

    file = open(file_name, 'r')

    for original_row in file:
        row = get_row_as_dict(original_row, False)
        # If not, just do nothing
        if row[PITCHER].lower() == pitcher_name:
            if row[PITCH_VALUE] != '':
                pitches.append(int(row[PITCH_VALUE]))

                if previous_pitch is not None:
                    deltas.append(int(row[PITCH_VALUE]) - int(previous_pitch))
                previous_pitch = row[PITCH_VALUE]

    file.close()
    # return pitches
    return pitches, deltas

'''
Uses a Google Spreadsheet ID and a pitcher name to analyze to fetch all of pitches thrown by the named person
and then return them all in the order they were thrown, as well as the "Deltas" between the pitches - that is, the difference
between the values of each pitch thrown by that person.

These lists are commonly fed into the distributation analyzer stuff to produce reports about the pitches
'''
def fetchPitchesByPitcherAndGoogleSheet(spreadsheet_id, pitcher_name):
    spreadsheets = get_spreadsheet_service()

    pitches = []
    deltas = []
    pitcher_name = pitcher_name.lower()
    previous_pitch = None
    # for sheet in sheets:
    # print(sheet.get('properties').get('title'))
    # if sheet.get('properties').get('title') == 'Tables':
    #     continue
    result = spreadsheets.values().get(spreadsheetId=spreadsheet_id, range="All PA's").execute()
    values = result.get('values')

    row_number = 1
    for row in values:
        if len(row) >= 19 and row_number >= 2:
            converted_row = get_row_as_dict(row, mlr=True)
            if converted_row[PITCHER].lower() == pitcher_name:
                if converted_row[PITCH_VALUE] != '':
                    pitches.append(int(converted_row[PITCH_VALUE]))

                    if previous_pitch is not None:
                        deltas.append(int(converted_row[PITCH_VALUE]) - int(previous_pitch))
                    previous_pitch = converted_row[PITCH_VALUE]
        else:
            row_number += 1
    return pitches, deltas


if __name__ == '__main__':
    # MLN
    pitches, deltas = fetchPitchesByPitcherAndLocalFile("/home/george/Documents/mlnReports/mln_master_log_combined.csv", 'Jordan Peppers')

    #MLR
    # pitches,deltas = analyzePitcher("/home/george/Downloads/MLR3.csv", 'Caleb Miller')
    #
    #
    result = groupValuesByRange(deltas,range_size=100, numbers=[-999,1001])
    print(result)