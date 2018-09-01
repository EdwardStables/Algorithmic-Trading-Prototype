import sys
import os
import subprocess
from PyQt4 import QtCore, QtGui, uic
import pandas as pd 

dir_path = os.path.dirname(os.path.realpath(__file__))
qtCreatorFile = dir_path + "\\GUI.ui" # Enter file here.
#testing branch 
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
 

######################################################################
#                                                                    #
# Sets up the main GUI and the basic data actions within the program #
#                                                                    #
######################################################################

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
        self.setDataListContext()
        

        #####################
        #Interaction methods run
        self.data_list.clicked.connect(self.data_item_clicked)
        self.drop_data_addData.triggered.connect(self.addData)
        
        
    def setDataListContext(self):
        self.data_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.data_list.connect(self.data_list, QtCore.SIGNAL("customContextMenuRequested(QPoint)"), self.data_list_context)

    def data_list_context(self, QPos):
        self.listMenu = QtGui.QMenu()
        remove = self.listMenu.addAction("Remove")
        add_path = self.listMenu.addAction("Add Path")
        show_in_file_explorer = self.listMenu.addAction("Show In File Explorer")

        current_index = self.data_list.selectedIndexes()[0]
        current_name = current_index.model().itemFromIndex(current_index).text()

        self.connect(remove, QtCore.SIGNAL("triggered()"), lambda item = current_name: self.removedClicked(item))
        self.connect(add_path, QtCore.SIGNAL("triggered()"), lambda item = current_name: self.add_pathClicked(item))
        self.connect(show_in_file_explorer, QtCore.SIGNAL("triggered()"), lambda item = current_name: self.show_in_file_explorerClicked(item))

        name_list = []
        for i in self.location_list:
            name_list.append(i.name)

        if current_name in name_list:
            add_path.setEnabled(False)
            show_in_file_explorer.setEnabled(True)
        else:
            add_path.setEnabled(True)
            show_in_file_explorer.setEnabled(False)
        
        parentPosition = self.data_list.mapToGlobal(QtCore.QPoint(0,0))
        self.listMenu.move(parentPosition + QPos)
        self.listMenu.show()

    def removedClicked(self, item):
        #removes the selected dataset, removes reference to it from all relevant places
        
        print(item)
        for i in self.location_list:
            if i.name == item:
                self.location_list.remove(i)
                break
                
        data_locations = pd.read_csv(dir_path + "\\dataSets.csv", index_col = False)
        data_locations = data_locations[data_locations.File_Name != item]
        data_locations.to_csv(dir_path + '\\dataSets.csv', index=False)
        self.setTableContent("")
        self.dataList.removeRow(item)
    


    def add_pathClicked(self, item):
        #Allows the user to re-add missing datasets that have been renamed/moved since last launching the platform
        self.addData()
        self.removedClicked(item)
    
    
    def show_in_file_explorerClicked(self, item):
        #Brings up the file explorer leading to the file in question when 'show in file explorer' is selected in the context menu.
        data_locations = pd.read_csv(dir_path + "\\dataSets.csv", index_col = False)
        pd.set_option("display.max_colwidth", 10000)
        location = data_locations.File_Location[data_locations.File_Name == item].to_string(index = False)
        string = 'explorer /select,"'+ location + '"'
        print(string)
        subprocess.Popen(string)


    def setDataListContent(self):
        #Reads dataSets.csv (contains all of the file names and paths)
        #Saves filenames and data as a single array within the program
        #Adds the filenames to the listview model
        data_locations = pd.read_csv(dir_path + "\\dataSets.csv")
        size = data_locations.shape
        location_error = []
        for i in range (size[0]):
            name = str(data_locations.iloc[i, 0])
            try:
                text = pd.read_csv(data_locations.iloc[i, 1])
                self.location_list.append(data_set(name, text))
            except:
                location_error.append(name)
        for p in self.location_list:
            print(type(p.name))
            self.dataList.addRow(p.name)
        for p in location_error:
            self.dataList.addBoldrow(p)
        
        if location_error: 
            self.error_message("The bold highlighted datasets appear to have moved location. Please add them back.")


    def data_item_clicked(self, index):
        #when an item is selected in the datalist then the corresponding data is shown in the tableview
        for i in self.location_list:
            if index.data() == i.name:
                self.setTableContent(i.text)
                break
        else:
            self.setTableContent("")

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

    def error_message(self, message):
        msgBox = QtGui.QMessageBox(self)
        msgBox.setWindowTitle("Error")
        msgBox.setText(message)
        msgBox.addButton(QtGui.QMessageBox.Ok)
        msgBox.setDefaultButton(QtGui.QMessageBox.Ok)
        ret = msgBox.exec_()


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
    
    def addBoldrow(self, item):
        item = QtGui.QStandardItem(item)
        f = item.font()
        f.setBold(True)
        item.setFont(f)
        self.model.appendRow(item)

    def removeRow(self, name):
        for item in self.model.findItems(name):
            self.model.removeRow(item.row())

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