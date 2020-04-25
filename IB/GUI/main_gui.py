from GUI.mainwindow import Ui_MainWindow
from PyQt5 import QtWidgets, QtCore, QtGui
import sys
import qdarkstyle
from get_finance_info_from_api import get_symbol, get_stock_info, get_stock_list_percent_change, \
    get_stock_pct_change_history
import pandas as pd
from functools import partial
from send_mail import send_mail
from datetime import datetime
class Mainwindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(Mainwindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton_refresh.clicked.connect(self.stock_research)
        self.ui.lineEdit_symbol_search.returnPressed.connect(self.symbol_search)
        self.ui.pushButton_search.clicked.connect(self.symbol_search)
        self.ui.pushButton_refresh_compare.clicked.connect(self.stock_compare)
        self.ui.pushButton_monitor_compare.clicked.connect(self.stock_monitor)
        self.isMonitor = False
        self.stock_print = dict()
        self.stock_last_price = dict()
        self.df_watch_list = pd.read_csv('watch_list.csv')
    def symbol_search(self):
        try:
            str_input = self.ui.lineEdit_symbol_search.text().strip()
            df_info = get_symbol(str_input)
            model = PandasModel(df_info)
            self.ui.tableView_symbol.setModel(model)
            self.ui.tableView_symbol.resizeColumnsToContents()
        except Exception as e:
            self.warning_message(e)



    def stock_compare(self):
        try:
            name = self.ui.lineEdit_symbol_input_compare.text().strip()
            change = self.ui.lineEdit_change_input_compare.text().strip()
            df_show, df_reserve = get_stock_pct_change_history(name, change)
            self.ui.tableWidget_compare.setColumnCount(df_show.shape[1])
            self.ui.tableWidget_compare.setRowCount(df_show.shape[0])
            self.ui.tableWidget_compare.setHorizontalHeaderLabels(list(df_show.columns))
            self.ui.tableWidget_compare.setVerticalHeaderLabels(list(df_show.index))
            for i in range(df_show.shape[0]):
                for j in range(df_show.shape[1]):
                    self.ui.tableWidget_compare.setItem(i, j, QtWidgets.QTableWidgetItem(str(df_show.iloc[i, j])))
                    if self.ui.tableWidget_compare.verticalHeaderItem(i).text() in df_reserve.index:
                        self.ui.tableWidget_compare.item(i, j).setBackground(QtGui.QColor(100, 100, 150))

            self.ui.tableWidget_compare.resizeColumnsToContents()
        except Exception as e:
            self.warning_message(e)

    def loop_function(self, stock_last_price, df):
        self.stock_print = get_stock_list_percent_change(stock_last_price, df)
        self.stock_print['MA'] = 0.02*100
        if not self.stock_print == False:
            for keys, values in self.stock_print.items():
                df_show, df_reserve = get_stock_pct_change_history(keys, values)
                df_show['Stock'] = keys
                df_show['current_change'] = values
                self.ui.tableWidget_compare.setColumnCount(df_show.shape[1])
                self.ui.tableWidget_compare.setRowCount(df_show.shape[0])
                self.ui.tableWidget_compare.setHorizontalHeaderLabels(list(df_show.columns))
                self.ui.tableWidget_compare.setVerticalHeaderLabels(list(df_show.index))
                for i in range(df_show.shape[0]):
                    for j in range(df_show.shape[1]):
                        self.ui.tableWidget_compare.setItem(i, j, QtWidgets.QTableWidgetItem(str(df_show.iloc[i, j])))
                content = df_show.to_html()
                subject = str(datetime.today().date()) + ' :' + str(keys) + " move: " + str(values)
                send_mail(subject, content)

    def get_last_price(self):
        df = pd.read_csv('watch_list.csv')

        for stock_high_vol, stock_low_vol in zip(df['high_vol'], df['low_vol']):
            if stock_high_vol not in self.stock_last_price.keys() and stock_low_vol not in self.stock_last_price.keys():
                self.stock_last_price[stock_high_vol] = \
                    get_stock_info(function='stock_daily', name=stock_high_vol, interval=None)['4. close'][-1]
                self.stock_last_price[stock_low_vol] = \
                    get_stock_info(function='stock_daily', name=stock_low_vol, interval=None)['4. close'][-1]

        return self.stock_last_price

    def stock_monitor(self):
        if not self.isMonitor:
            self.isMonitor = True
            self.ui.pushButton_monitor_compare.setText('Stop')
            self.get_last_price()
            self.timer = QtCore.QTimer()
            self.timer.setInterval(60000)
            #self.loop_function(self.stock_last_price,self.df_watch_list)
            self.timer.timeout.connect(partial(self.loop_function, self.stock_last_price, self.df_watch_list))

            self.timer.start()
        else:
            self.isMonitor = False
            self.ui.pushButton_monitor_compare.setText('Monitor')
            self.timer.stop()

        print('done')


    def stock_research(self):
        try:
            function = self.ui.comboBox_stock.currentText()
            interval = None
            if 'intraday' in function:
                interval = self.ui.comboBox_interval.currentText()
            name = self.ui.lineEdit_symbol_input_1.text()
            df_info = get_stock_info(function, name, interval)
            model = PandasModel(df_info)
            # self.ui.tableView_main
            self.ui.tableView_main.setModel(model)
            '''
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self.stock_research)
            self.timer.start(10000)
            '''
        except Exception as e:
            self.warning_message(e)


    def warning_message(self, message):
        myMessageBox = QtWidgets.QMessageBox.warning(self, 'Error', str(message))

        self.show()

        print('')


class PandasModel(QtCore.QAbstractTableModel):
    def __init__(self, df=pd.DataFrame(), parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent=parent)
        self._df = df.copy()

    def toDataFrame(self):
        return self._df.copy()

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        if orientation == QtCore.Qt.Horizontal:
            try:
                return self._df.columns.tolist()[section]
            except (IndexError,):
                return QtCore.QVariant()
        elif orientation == QtCore.Qt.Vertical:
            try:
                # return self.df.index.tolist()
                return self._df.index.tolist()[section]
            except (IndexError,):
                return QtCore.QVariant()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        if not index.isValid():
            return QtCore.QVariant()

        return QtCore.QVariant(str(self._df.ix[index.row(), index.column()]))

    def setData(self, index, value, role):
        row = self._df.index[index.row()]
        col = self._df.columns[index.column()]
        if hasattr(value, 'toPyObject'):
            # PyQt4 gets a QVariant
            value = value.toPyObject()
        else:
            # PySide gets an unicode
            dtype = self._df[col].dtype
            if dtype != object:
                value = None if value == '' else dtype.type(value)
        self._df.set_value(row, col, value)
        return True

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._df.index)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self._df.columns)

    def sort(self, column, order):
        colname = self._df.columns.tolist()[column]
        self.layoutAboutToBeChanged.emit()
        self._df.sort_values(colname, ascending=order == QtCore.Qt.AscendingOrder, inplace=True)
        self._df.reset_index(inplace=True, drop=True)
        self.layoutChanged.emit()


app = QtWidgets.QApplication([])
application = Mainwindow()
app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
application.show()
sys.exit(app.exec())
