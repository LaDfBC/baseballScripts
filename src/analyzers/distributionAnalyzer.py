import pandas as pd
from src.displayers import standardOutWriter

numbers = [1, 1001]

# Uses PANDAS to group numbers by a given range
def groupByRange(data, range=100):
    ranges = []
    i = numbers[0]

    # Sets range
    while i <= numbers[1]:
        ranges.append(i)
        i = i + range

    df = pd.DataFrame({'data': data})

    # Does the actual thing - cuts the data into pieces and then grousp it
    cuts = pd.cut(df['data'], ranges)
    df2 = df.groupby(cuts)['data'].agg(['count'])

    # cuts = pd.cut(data, ranges)
    return df2

data = [1, 101, 201, 103, 600]

standardOutWriter.writeToStandardOut(groupByRange(data, 50))
