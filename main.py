import datetime
import datetime as dt
import sqlite3
import sys

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QApplication, \
    QMainWindow, QTableWidgetItem, QPushButton, \
    QLineEdit, QInputDialog
from PyQt5.QtWidgets import QDateEdit

# from motocycle import Moto, Work
from design import Ui_MainWindow


class Moto:
    def __init__(self, name, db_id=-1):
        self.id = db_id
        self.moto_nazvanie = name
        self.histories = []

    def add_history(self, hitory):
        self.histories.append(hitory)


class Work:
    def __init__(self, date=datetime.datetime.now(), work='', mhc=0., cost=0):
        self.name = work
        self.date = date
        self.mhc = mhc
        self.cost = cost

    def __str__(self):
        return ':'.join([self.name, self.date, self.mhc, self.cost])

    def load(self, s):
        ':'.split(s)


sqlite_select_one_moto = """SELECT * FROM motos WHERE name = ? """
sqlite_insert_one_moto = """INSERT INTO motos(name) VALUES(?)  """
sqlite_select_all_work = """SELECT * FROM works WHERE id_moto = ?"""
sqlite_insert_one_work = """INSERT INTO works(id_moto, date, work_name, moto_hour, cost) VALUES (?, ?, ?, ?, ?)"""


class MyWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        QMainWindow.__init__(self)

        self.setupUi(self)
        self.my_setupUi()

        self.pushButton_add_mot_nazvanie.clicked.connect(self.button_add_moto)
        self.pushButton_add_histori.clicked.connect(self.button_add_work)
        self.pushButton_add_info.clicked.connect(self.show_info_visible)
        self.comboBox_moto_nazvanie.activated.connect(self.get_current_moto)
        self.pushButton_add_works.clicked.connect(self.show_dialog)
        self.connection = sqlite3.connect("garage_moto.db",
                                          detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)

        self.current_moto = None

        self.moto_hour = ''
        self.data = ''
        self.current = ''

        self.name_moto = []
        self.name = []

        self.n = 0
        self.cost = 0
        self.id_moto = 0

        self.get_all_motos()
        self.update_motonames_combobox()
        self.get_current_moto()

    def init_ui_trash(self):
        self.btn = QPushButton('Dialog', self)
        self.btn.move(20, 20)
        self.btn.clicked.connect(self.show_dialog)

        self.stroka_add = QLineEdit(self)
        self.stroka_add.move(130, 220)

        self.setGeometry(300, 300, 290, 150)
        self.setWindowTitle('выбрать действие')
        self.show()

    def show_dialog(self):
        text, ok = QInputDialog.getText(self, 'выбрать действие', 'выберете действие:')

        if ok:
            self.lineEdit_work.setText(str(text))

    def get_current_moto(self):
        cur = self.connection.cursor()
        result = cur.execute(sqlite_select_one_moto, (self.comboBox_moto_nazvanie.currentText(),)).fetchone()

        self.current_moto = Moto(result[1], result[0])

        result_works = cur.execute(sqlite_select_all_work, (self.current_moto.id,)).fetchall()

        for work in result_works:
            # print(work)
            self.current_moto.add_history(Work(work[2], work[3], work[4], work[5]))

        self.update_table()

    def button_add_moto(self):
        moto = Moto(self.lineEdit_moto_nazvanie.text())
        self.name_moto.append(moto)

        cur = self.connection.cursor()
        cur.execute(sqlite_insert_one_moto, (moto.moto_nazvanie,))
        self.connection.commit()

        self.lineEdit_moto_nazvanie.setText('')

        self.get_all_motos()
        self.update_motonames_combobox()

    def button_add_work(self):
        if self.current_moto is None:
            return

        work_name = self.lineEdit_work.text()
        cost_text = self.lineEdit_cost.text()
        moto_hour_text = self.lineEdit_moto_hours.text()
        q_date = self.dateEdit.date()
        date_work = datetime.date(q_date.year(), q_date.month(), q_date.day())
        # print(f'Q_date: {date_work}')

        if work_name == '':
            self.lineEdit_work.setText('пустая строка')
            return

        elif work_name.isdigit():
            self.lineEdit_work.setText('числа недопустимы')
            return

        elif not work_name == 'замена масла' or \
                work_name == 'обслуживание воздушного фильтра' or \
                work_name == 'замена воздушного фильтра' or \
                work_name == 'замена топливного фильтра' or \
                work_name == 'замена антифриза' or \
                work_name == 'замена свечей' or \
                work_name == 'подтяжка, смазка цепи' or \
                work_name == 'чистка и синхронизация карбюратора' or \
                work_name == 'промывка и пропитка обслуживаемого воздушного фильтра' or \
                work_name == 'замена подшибников':
            pass

        if cost_text == '':
            self.lineEdit_cost.setText('пустая строка')
            return

        elif int(cost_text) <= 0:
            self.lineEdit_cost.setText('цена не может быть меньше нуля')
            return

        elif not cost_text.isdigit():
            self.lineEdit_cost.setText('тут должно быть число')
            return

        if moto_hour_text == '':
            self.lineEdit_moto_hours.setText('пустая строка')
            return

        elif not moto_hour_text.isdigit():
            self.lineEdit_moto_hours.setText('тут должно быть число')
            return

        elif int(moto_hour_text) <= 0:
            self.lineEdit_moto_hours.setText('моточасов не может быть меньше нуля')
            return


        cur = self.connection.cursor()
        cur.execute(sqlite_insert_one_work, (self.current_moto.id, date_work, work_name,
                                             int(moto_hour_text), int(cost_text)))

        self.connection.commit()
        self.lineEdit_work.setText('')
        self.lineEdit_moto_hours.setText('')
        self.lineEdit_cost.setText('')

        self.get_current_moto()

    def show_info_visible(self):
        if self.lineEdit_info.isVisible():
            self.lineEdit_info.setVisible(False)
        else:
            self.lineEdit_info.setVisible(True)

    def update_table(self):

        self.setMinimumSize(QSize(500, 80))  # Set sizes

        self.tableWidget_histori.setColumnCount(4)  # количество колонок ---------------------------------
        self.tableWidget_histori.setRowCount(len(self.current_moto.histories))  # количество строк ------
        self.tableWidget_histori.setHorizontalHeaderLabels(
            ["ДАТА", "ДЕЙСТВИЕ", "МОТОЧАСОВ", "СУММА"])  # колонки -------------

        # выравнивание заголовков ========
        self.tableWidget_histori.horizontalHeaderItem(0).setTextAlignment(
            Qt.AlignHCenter)  # выравнивание заголовков ========
        self.tableWidget_histori.horizontalHeaderItem(1).setTextAlignment(
            Qt.AlignHCenter)  # выравнивание заголовков ========
        self.tableWidget_histori.horizontalHeaderItem(2).setTextAlignment(
            Qt.AlignHCenter)  # выравнивание заголовков ========
        self.tableWidget_histori.horizontalHeaderItem(3).setTextAlignment(
            Qt.AlignHCenter)  # выравнивание заголовков ========
        # print(self.current_moto.histories)

        for i, work in enumerate(self.current_moto.histories):
            # print(f'db_date: {work.date}')
            self.tableWidget_histori.setItem(i, 0, QTableWidgetItem(str(work.date)))
            self.tableWidget_histori.setItem(i, 1, QTableWidgetItem(work.name))
            self.tableWidget_histori.setItem(i, 2, QTableWidgetItem(str(work.mhc)))
            self.tableWidget_histori.setItem(i, 3, QTableWidgetItem(str(work.cost)))
            # print(work.date, work.name, work.mhc, work.cost, sep='\t')

        self.tableWidget_histori.resizeColumnsToContents()

    def update_motonames_combobox(self):
        self.comboBox_moto_nazvanie.clear()

        for i in self.name_moto:
            self.comboBox_moto_nazvanie.addItem(str(i.moto_nazvanie))

    def get_all_motos(self):
        self.name_moto = []
        cur = self.connection.cursor()

        # Выполнение запроса и получение всех результатов
        result = cur.execute("""SELECT * FROM motos""").fetchall()
        # Вывод результатов на экран
        for elem in result:
            moto = Moto(elem[1], db_id=elem[0])
            self.name_moto.append(moto)

    def my_setupUi(self):
        self.dateEdit = QDateEdit(self)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.dateEdit.setStyleSheet("background-color: #f0fff")
        self.dateEdit.setFont(font)
        self.dateEdit.setCalendarPopup(True)
        self.dateEdit.setTimeSpec(QtCore.Qt.LocalTime)
        self.dateEdit.setGeometry(QtCore.QRect(240, 140, 131, 27))  # +++
        date = dt.datetime.now()
        self.dateEdit.setDate(QtCore.QDate(date.year, date.month, date.day))

        self.lineEdit_info.setText('Информация о допустимых действиях в README.txt')
        self.lineEdit_info.setVisible(False)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
