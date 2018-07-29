import sys
import os
from PyQt4 import QtCore, QtGui, uic
import pandas as pd 

dir_path = os.path.dirname(os.path.realpath(__file__))
qtCreatorFile = dir_path + "\\GUI.ui" # Enter file here.
#interpret branch
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
 
class MyApp(QtGui.QMainWindow, Ui_MainWindow):

    location_list = []
    dataList = None

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        
        #####################
        #Initialisation methods run       
        #self.showMaximized()
        self.visulise_image.setPixmap(QtGui.QPixmap(dir_path + "\\duck.jpg"))
        self.dataList = datalistModel(self.data_list)
        self.setDataListContent()
        

        #####################
        #Interaction methods run
        self.data_list.clicked.connect(self.data_item_clicked)
        self.drop_data_addData.triggered.connect(self.addData)
        

    def setDataListContent(self):
        #Reads dataSets.csv (contains all of the file names and paths)
        #Saves filenames and data as a single array within the program
        #Adds the filenames to the listview model
        data_locations = pd.read_csv(dir_path + "\\dataSets.csv")
        size = data_locations.shape
        for i in range (size[0]):
            name = str(data_locations.iloc[i, 0])
            text = pd.read_csv(data_locations.iloc[i, 1])
            self.location_list.append(data_set(name, text))
        for p in self.location_list:
            self.dataList.addRow(p.name)

    def data_item_clicked(self, index):
        #when an item is selected in the datalist then the corresponding data is shown in the tableview
        for i in self.location_list:
            if index.data() == i.name:
                self.setTableContent(i.text)
                break

    def addData(self):
        #handles when the file explorer selects a new file.
        #adds to the storage CSV, the program array, and adds it to the listview model
        openfile = QtGui.QFileDialog.getOpenFileName(self, filter = "CSV files (*.csv)")
        openfile = openfile.replace("/", "\\")
        data_locations = pd.read_csv(dir_path + "\\dataSets.csv")
        location_list = data_locations['File_Location'].tolist()
        
        if openfile not in location_list:
            name = openfile.split("\\")[-1]
            name = name.split(".")[0]
            line = pd.DataFrame([[name, openfile]], columns = ['File_Name', 'File_Location'])
            new = data_locations.append(line)
            new.to_csv(dir_path + '\\dataSets.csv', index=False)
            self.location_list.append(data_set(name, pd.read_csv(openfile)))
            self.dataList.addRow(name)
        else:
            print("Already in there") 
            QtGui.QMessageBox.information(self, "!", "This CSV is already loaded.")   
        
    def setTableContent(self, text):
        #handles creating and displaying the table model when a new item is selected
        model = tableModel(text)
        #model.setHorizontalHeaderLables(text[0])
        self.data_table.setModel(model)


class data_set():
    #a simple data type with the name and data, used for the list of all names and data in MyApp()
    def __init__(self, name=None, text=None):
        self.name=name
        self.text=text

class datalistModel():
    #a simple model used for the listView of data titles. 
    model = None
    data_list = None
    def __init__(self, data_list):
        #creates the model
        self.data_list = data_list
        self.model = QtGui.QStandardItemModel()
        self.data_list.setModel(self.model)
    
    def addRow(self, item):
        #adds the selected row to the model
        item = QtGui.QStandardItem(item)
        self.model.appendRow(item)

    def clear(self):
        #clears everything in the model
        self.model.removeRow(0, self.model.rowCount())

class tableModel(QtCore.QAbstractTableModel):
    #class produces a model for the input pandas dataframe
    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self,parent)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]
    
    def columnCount(self, parent=None):
        return self._data.shape[1]
    
    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
            return None    



 
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())