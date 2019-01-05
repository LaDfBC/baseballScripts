import pandas as pd
from src.displayers import standardOutWriter

# Uses PANDAS to group numbers by a given range
def groupValuesByRange(data, range_size=100, numbers=None):
    #  Allow the passing in of an array, but default to this
    if numbers is None:
        numbers = [1, 1001]

    ranges = __getRangeArray__(numbers, range_size)

    df = pd.DataFrame({'data': data})

    # Does the actual thing - cuts the data into pieces and then groups it
    cuts = pd.cut(df['data'], ranges)
    df2 = df.groupby(cuts)['data'].agg(['count'])

    return df2

def analyzeStreak(data, range_size = 100, numbers=None):
    df = pd.DataFrame({'data': data})
    df['last_delta'] = df['data'].shift(1)

    ranges = __getRangeArray__(numbers, range_size)

    last_cuts = pd.cut(df['last_delta'], ranges)
    data_cuts = pd.cut(df['data'], ranges)

    df_counted = pd.DataFrame({'last_cuts': last_cuts, 'normal_cuts':data_cuts})
    df_counted.groupby(['normal_cuts', 'last_cuts']).size() # Better
    finished_df = df_counted.pivot(index='normal_cuts', columns=ranges, values='last_cuts').plot(kind='bar')

    return finished_df

# Does some preprocessing and then calls out to the range function, with the set list of deltas
def fetchDeltasByRange(data, range_size=100):
    numbers = [-999, 1001]

    deltas = []
    previous = None
    for value in data:
        if previous is not None:
            deltas.append(value - previous)
        previous = value

    return groupValuesByRange(deltas, range_size, numbers)

# Helper method that splits the numbers into a set specified by the range
def __getRangeArray__(numbers, range_size):
    ranges = []
    i = numbers[0]

    # Sets range
    while i <= numbers[1]:
        ranges.append(i)
        i = i + range_size

    return ranges

# data = [730, 916, 413, 187, 530, 259, 853, 85, 831, 831, 93, 888, 947, 643, 238, 348, 699, 209, 361, 777, 543, 61, 973, 631, 732, 85, 888, 71, 808, 42, 778, 105, 644, 738, 682,]

# standardOutWriter.writeToStandardOut(groupValuesByRange(data, 100))