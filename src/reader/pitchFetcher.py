from src.analyzers.distributionAnalyzer import groupValuesByRange, analyzeStreak
from src.reader.googleSheetsUtil import get_spreadsheet_service
from src.spreadsheet.row_organizer import PITCHER, PITCH_VALUE, get_row_as_dict

'''
Uses a filename on the local machine and a pitcher name to analyze to fetch all of pitches thrown by the named person
and then return them all in the order they were thrown, as well as the "Deltas" between the pitches - that is, the difference
between the values of each pitch thrown by that person.

These lists are commonly fed into the distributation analyzer stuff to produce reports about the pitches
'''
def fetchPitchesByPitcherAndLocalFile(file_name, pitcher_name, mlr = False):
    pitches = []
    deltas = []

    pitcher_name = pitcher_name.lower()
    previous_pitch = None

    file = open(file_name, 'r')

    for original_row in file:
        row = get_row_as_dict(original_row, mlr, is_list=False)
        # If not, just do nothing
        if PITCHER in row.keys() and row[PITCHER].lower() == pitcher_name:
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
def fetchPitchesByPitcherAndGoogleSheet(spreadsheet_id, pitcher_name, mlr=False):
    spreadsheets = get_spreadsheet_service()

    pitches = []
    deltas = []
    pitcher_name = pitcher_name.lower()
    previous_pitch = None

    result = spreadsheets.values().get(spreadsheetId=spreadsheet_id, range="All PAs").execute()
    values = result.get('values')
    row_number = 1

    for row in values:
        if len(row) >= 19 and row_number >= 2:
            converted_row = get_row_as_dict(row, mlr, is_list=True)
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
    pitches, deltas = fetchPitchesByPitcherAndLocalFile("/home/george/Downloads/mlnmaster1.csv", 'Thomas Nova')
    pitches_s2, deltas_s2 = fetchPitchesByPitcherAndGoogleSheet('1vR8T-nZwJFYj8yKDwt0999FHzfZEEfFArZ2m1OsxPx8', 'Thomas Nova')

    pitches = pitches + pitches_s2
    deltas = deltas + deltas_s2

    #MLR
    # pitches,deltas = fetchPitchesByPitcherAndGoogleSheet("2PACX-1vTxYUfunWgHW9Zcm2vg4VcCI_oEv9_PQ_3sOTXFyJ8KZc3dpg7P-OReyNFC9_0E5G_KXQq5vAmQYhCC", 'Thomas Nova', mlr=True)
    #
    #
    # result = groupValuesByRange(deltas,range_size=100, numbers=[-999,1001])
    result = analyzeStreak(deltas, range_size=100, numbers=[-999,1001])
    print(result)