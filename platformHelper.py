import os
import pandas as pd
import numpy as np
#contains all of the interface methods between the platform and the algorithm
dir_path = os.path.dirname(os.path.realpath(__file__))
print(dir_path)
data_list = {}

def getDataList():
    _updateData()
    name_list = []
    for i in data_list:
        name_list.append(i)
    return name_list

def getData(name = None):
    _updateData()
    dataSet = None
    if name in data_list:
        dataSet = pd.read_csv(data_list[name])
    return dataSet

def setData(name, dataSet):
    _updateData()

    if name in data_list:
        dataSet.to_csv(data_list[name])
    else:
        newLocation = dir_path + "\\User_Datasets\\" + name + ".csv"
        dataSet.to_csv(newLocation)
        dataDF = pd.read_csv(dir_path + "\\dataSets.csv")

        line = pd.DataFrame([[name, newLocation]], columns = ['File_Name', 'File_Location'])
        new = dataDF.append(line)
        new.to_csv(dir_path + "\\dataSets.csv", index = False)


        

def _updateData():
    dataDF = pd.read_csv(dir_path + "\\dataSets.csv")
    for index, row in dataDF.iterrows():
        if row["File_Name"] not in data_list:
            data_list[row["File_Name"]] = row["File_Location"]

if __name__== "__main__":
    getData()
