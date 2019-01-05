# Dataframe from PANDAS
def writeToStandardOut(dataFrame):
    for data in dataFrame.iterrows():
        print(str(data[0].left) + "," + str(data[0].right) + "," + str(data[1]['count']))

def writeToFile(dataFrame, fileName):
    file = open(fileName, 'w')
    for data in dataFrame.iterrows():
        file.write(str(data[0].left) + "," + str(data[0].right) + "," + str(data[1]['count']) + "\n")

    file.close()
