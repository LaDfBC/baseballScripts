from src.analyzers.distributionAnalyzer import groupByRange
from src.spreadsheet.row_organizer import PITCHER, PITCH_VALUE, GAME_NUMBER, get_row_as_dict


def analyzePitcher(file_name, pitcher_name):
    pitches = []
    deltas = []

    pitcher_name = pitcher_name.lower()
    previous_pitch = None
    previous_pitch_game = None

    file = open(file_name, 'r')

    for original_row in file:
        row = get_row_as_dict(original_row)
        # If not, just do nothing
        if row[PITCHER].lower() == pitcher_name:
            if row[PITCH_VALUE] != '':
                pitches.append(int(row[PITCH_VALUE]))

                if previous_pitch is not None and previous_pitch_game == row[GAME_NUMBER]:
                    deltas.append(int(row[PITCH_VALUE]) - int(previous_pitch))
                previous_pitch = row[PITCH_VALUE]
                previous_pitch_game = row[GAME_NUMBER]

    file.close()
    return pitches, deltas

pitches, deltas = analyzePitcher("/home/george/Documents/mlnReports/mln_master_log_combined.csv", 'Bartholomew Crumblepuff')

result = groupByRange(deltas)
print(result)