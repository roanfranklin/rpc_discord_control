#!/usr/bin/python3

from PyQt5 import (QtWidgets, QtGui, QtCore, uic)
from PyQt5.QtWidgets import (QApplication, QWidget, QToolTip, QPushButton, QMessageBox,
                            QDesktopWidget, QInputDialog, QTableWidgetItem, QFileDialog,
                            QSystemTrayIcon, QAction, QStyle, QMenu, qApp,
                            QLineEdit)
from PyQt5.QtCore import (Qt, QUrl, QSize, QFile, QDir)
from PyQt5.QtGui import (QPixmap, QIcon, QFont, QPalette, QColor)

import sys
import os
import time

import requests

from pypresence import Presence

DIR_APP = '{0}'.format(os.path.dirname(os.path.realpath(__file__)))

from src.database import *
from src.git import *
from src.icons import *

RPC = Presence('', pipe=0, loop=None, handler=None)

APP_TITLE = 'RPC Discord Control'
APP_TITLE_COMPLETE = 'Rich Presence Discord'
APP_AUTHOR = 'Roan Franklin'
APP_EMAIL =  'roanfranklin@gmail.com'
APP_SITE = 'https://www.remf.com.br/'
APP_VERSION = git_version(DIR_APP)
APP_GIT_STATUS = git_status(DIR_APP)
status_quit = False
debug = False


class frmMain(QtWidgets.QMainWindow):
    check_box = None
    tray_icon = None

    def __init__(self):
        super(frmMain, self).__init__()
        uic.loadUi('{0}/ui/frmMain.ui'.format(DIR_APP), self)

        initial_sqlite(DIR_APP)

        self.CONNECTED = False
        self.CONNECTED_index = -1

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(icon_app(DIR_APP))

        show_action = QAction("Show", self)
        hide_action = QAction("Hide", self)
        quit_action = QAction("Exit", self)
        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.__app_hide)
        quit_action.triggered.connect(self.__app_quit)
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        tray_menu2 = QMenu()
        tray_menu2.addAction(hide_action)
        tray_menu2.addAction(quit_action)

        self.twSaved = self.findChild(QtWidgets.QTableWidget, 'twSaved')
        self.twSaved.itemSelectionChanged.connect(self.twSavedSelectedClick)
        self.twSaved.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.twSaved.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.twSaved.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.twSaved.verticalHeader().setVisible(False)
        self.twSaved.horizontalHeader().setVisible(False)
        self.twSaved.setIconSize(QSize(44,44))
        self.twSaved.verticalHeader().setDefaultSectionSize(48)

        self.__InEnableSaved(False)

        try:
            rows = sqlite_query(DIR_APP, 'SELECT * FROM rpcsaved ORDER BY myorder ASC')
            self.twSaved.clearContents()
            if not debug:
                self.twSaved.setColumnHidden(0, True)
                self.twSaved.setColumnHidden(1, True)
            for row in rows:
                inx = rows.index(row)
                self.twSaved.insertRow(inx)

                ICON_RPC = icon_none(DIR_APP)

                self.twSaved.setItem(inx, 0, QtWidgets.QTableWidgetItem('{0}'.format(row['id'])))
                self.twSaved.setItem(inx, 1, QtWidgets.QTableWidgetItem('{0}'.format(row['myorder'])))
                self.twSaved.setItem(inx, 2, QtWidgets.QTableWidgetItem(ICON_RPC, row['name']))

                self.twSaved.selectRow(0)

                hVulnerabilities = self.twSaved.horizontalHeader()
                hVulnerabilities.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
                hVulnerabilities.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
                hVulnerabilities.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        except:
            self.__resetRPC()

        self.btnNew = self.findChild(QtWidgets.QToolButton, 'btnNew')
        self.btnNew.clicked.connect(self.__new)
        self.btnNew.setIcon(icon_plus(DIR_APP))
        self.btnNew.setToolTip("Add RPC")

        self.btnUp = self.findChild(QtWidgets.QToolButton, 'btnUp')
        self.btnUp.clicked.connect(self.btnUpVulnerabilityClicked)
        self.btnUp.setIcon(icon_up(DIR_APP))
        self.btnUp.setToolTip("Up item selected")

        self.btnDown = self.findChild(QtWidgets.QToolButton, 'btnDown')
        self.btnDown.clicked.connect(self.btnDownVulnerabilityClicked)
        self.btnDown.setIcon(icon_down(DIR_APP))
        self.btnDown.setToolTip("Down item selected")

        self.cbStartTime = self.findChild(QtWidgets.QCheckBox, 'cbStartTime')
        self.cbStartTime.setToolTip("Start time")
        self.cbEndTime = self.findChild(QtWidgets.QCheckBox, 'cbEndTime')
        self.cbEndTime.setToolTip("End time (stopwatch)")
        self.sbEndTime = self.findChild(QtWidgets.QSpinBox, 'sbEndTime')
        self.sbEndTime.setToolTip("Time [ Hours | Minutes | Seconds ]")
        self.rbHours = self.findChild(QtWidgets.QRadioButton, 'rbHours')
        self.rbHours.setToolTip("Hours")
        self.rbMinutes = self.findChild(QtWidgets.QRadioButton, 'rbMinutes')
        self.rbMinutes.setToolTip("Minutes")
        self.rbSeconds = self.findChild(QtWidgets.QRadioButton, 'rbSeconds')
        self.rbSeconds.setToolTip("Seconds")

        self.btnURLDev = self.findChild(QtWidgets.QToolButton, 'btnURLDev')
        self.btnURLDev.clicked.connect(self.btnURLDevClicked)
        self.btnURLDev.setIcon(icon_link(DIR_APP))
        self.btnURLDev.setToolTip("URL Applications Developers")

        self.btnSave = self.findChild(QtWidgets.QToolButton, 'btnSave')
        self.btnSave.clicked.connect(self.__save)
        self.btnSave.setIcon(icon_save(DIR_APP))
        self.btnSave.setToolTip("Save RPC")

        self.btnDelete = self.findChild(QtWidgets.QToolButton, 'btnDelete')
        self.btnDelete.clicked.connect(self.btnDeleteClicked)
        self.btnDelete.setIcon(icon_trash(DIR_APP))
        self.btnDelete.setToolTip("Delete RPC saved")

        self.btnConnect = self.findChild(QtWidgets.QToolButton, 'btnConnect')
        self.btnConnect.clicked.connect(self.__connect)
        self.btnConnect.setIcon(icon_offline(DIR_APP))
        self.btnConnect.setToolTip("Connect RPC")

        self.edtClientID = self.findChild(QtWidgets.QLineEdit, 'edtClientID')
        self.edtClientID.setToolTip("Client ID Rich Presence")
        self.cbLargeImage = self.findChild(QtWidgets.QComboBox, 'cbLargeImage')
        self.cbLargeImage.setToolTip("Large image")
        self.cbSmallImage = self.findChild(QtWidgets.QComboBox, 'cbSmallImage')
        self.cbSmallImage.setToolTip("Small image")
        self.edtDescription1 = self.findChild(QtWidgets.QLineEdit, 'edtDescription1')
        self.edtDescription1.setToolTip("Description1")
        self.edtDescription2 = self.findChild(QtWidgets.QLineEdit, 'edtDescription2')
        self.edtDescription2.setToolTip("Description2")
        self.cbButton1 = self.findChild(QtWidgets.QCheckBox, 'cbButton1')
        self.cbButton1.setToolTip("Insert button1")
        self.edtLabelButton1 = self.findChild(QtWidgets.QLineEdit, 'edtLabelButton1')
        self.edtLabelButton1.setToolTip("Label of button1")
        self.edtURLButton1 = self.findChild(QtWidgets.QLineEdit, 'edtURLButton1')
        self.edtURLButton1.setToolTip("URL of button1")
        self.cbButton2 = self.findChild(QtWidgets.QCheckBox, 'cbButton2')
        self.cbButton2.setToolTip("Insert button2")
        self.edtLabelButton2 = self.findChild(QtWidgets.QLineEdit, 'edtLabelButton2')
        self.edtLabelButton2.setToolTip("Label of button2")
        self.edtURLButton2 = self.findChild(QtWidgets.QLineEdit, 'edtURLButton2')
        self.edtURLButton2.setToolTip("URL of button2")

        self.btnAboutQt = self.findChild(QtWidgets.QToolButton, 'btnAboutQt')
        self.btnAboutQt.clicked.connect(self.__action_about_qt) 
        self.btnAboutQt.setIcon(icon_qt(DIR_APP))
        self.btnAboutQt.setToolTip("About Qt")

        self.btnAbout = self.findChild(QtWidgets.QToolButton, 'btnAbout')
        self.btnAbout.clicked.connect(self.__action_about) 
        self.btnAbout.setIcon(icon_question(DIR_APP))
        self.btnAbout.setToolTip("About App")

        self.btnClose = self.findChild(QtWidgets.QToolButton, 'btnClose')
        self.btnClose.setMenu(tray_menu2)
        self.btnClose.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.btnClose.setIcon(icon_quit(DIR_APP))
        self.btnClose.setToolTip("Hide/Exit")

        width = 862
        height = 501

        self.setWindowIcon(icon_app(DIR_APP))
        self.setWindowTitle('{0} ( {1} )'.format(APP_TITLE, APP_VERSION))

        self.setFixedWidth(width)
        self.setFixedHeight(height)

        self.center()
        self.setWindowFlag(QtCore.Qt.WindowMinMaxButtonsHint, False)
        self.__app_hide()
        #self.show()

    def closeEvent(self, event):
        if status_quit == False:
            event.ignore()
            self.__app_hide()
        else:
            event.accept()

    def center(self):
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        size = self.geometry()
        new_left = int((screen.width() - size.width()) / 2)
        new_top = int((screen.height() - size.height()) / 2)
        self.move(new_left, new_top)

    def __msg_error(self, TXT):
        QtWidgets.QMessageBox.warning(self, 'Error/Warning', TXT)

    def __action_about(self):
        QtWidgets.QMessageBox.about(self, 'About', f'<b>{APP_TITLE} - <i>{APP_TITLE_COMPLETE}</i></b><br><i>Version {APP_VERSION} {APP_GIT_STATUS}</i><br><br>Simple application of Rich Presence to Discord.<br><br><b>Author:</b> {APP_AUTHOR} - <i>{APP_EMAIL}</i><br><b>Web:</b> {APP_SITE}<br>')

    def __action_about_qt(self):
        QtWidgets.QMessageBox.aboutQt(self)
    
    def __app_hide(self):
        status_quit = False
        self.hide()
    
    def __app_quit(self):
        reply = QMessageBox.question(self, '{0} ( {1} )'.format(APP_TITLE, APP_VERSION), "Are you sure you want to quit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            status_quit = True
            qApp.quit()

    def twSavedSelectedClick(self):
        index=(self.twSaved.selectionModel().currentIndex())
        value=index.sibling(index.row(),0).data()
        self.__resetRPC()
        self.__loadRPC(value)

    def __new(self):
        txtRPCSaved, okPressed = QInputDialog.getText(self, '{0} ( {1} )'.format(APP_TITLE, APP_VERSION), 'Enter the name of the PRC :', QLineEdit.Normal, '')
        if okPressed and txtRPCSaved != '':
            self.__resetRPC()
            RPC_DATA = {'name': txtRPCSaved,
            'starttime': 0,
            'endtime': 0,
            'endtimevalue': 180,
            'endtimetype': 0,
            'idclient': 0,
            'largeimage': '',
            'largetext': '',
            'smallimage': '',
            'smalltext': '',
            'description1': '',
            'description2': '',
            'button1': 0,
            'button1name': '',
            'button1url': '',
            'button2': 0,
            'button2name': '',
            'button2url': ''}
            row, status = db_insertRPC(DIR_APP, RPC_DATA)

            inx = self.twSaved.rowCount()
            
            self.twSaved.insertRow(inx)

            self.twSaved.setItem(inx, 0, QtWidgets.QTableWidgetItem('{0}'.format(row['id'])))
            self.twSaved.setItem(inx, 1, QtWidgets.QTableWidgetItem('{0}'.format(row['myorder'])))
            self.twSaved.setItem(inx, 2, QtWidgets.QTableWidgetItem(icon_none(DIR_APP), txtRPCSaved))

            self.twSaved.selectRow(inx)

            hVulnerabilities = self.twSaved.horizontalHeader()
            hVulnerabilities.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
            hVulnerabilities.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
            hVulnerabilities.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
            self.__InEnableSaved(True)

            self.__resetRPC()
            self.__loadRPC(row['id'])
    
    def __resetRPC(self):
        self.cbStartTime.setChecked(False)
        self.cbEndTime.setChecked(False)
        self.sbEndTime.setValue(180)
        self.rbSeconds.setChecked(True)
        self.rbMinutes.setChecked(False)
        self.rbHours.setChecked(False)
        self.edtClientID.setText('')
        self.cbLargeImage.setCurrentText('')
        self.cbLargeImage.clear()
        self.cbSmallImage.setCurrentText('')
        self.cbSmallImage.clear()
        self.edtDescription1.setText('')
        self.edtDescription2.setText('')
        self.cbButton1.setChecked(False)
        self.edtLabelButton1.setText('')
        self.edtURLButton1.setText('')
        self.cbButton2.setChecked(False)
        self.edtLabelButton2.setText('')
        self.edtURLButton2.setText('')
        self.__checkRPC()

    def __InEnableSaved(self, OP = False):
        self.btnSave.setEnabled(OP)
        self.btnDelete.setEnabled(OP)
        self.btnConnect.setEnabled(OP)
        self.cbStartTime.setEnabled(OP)
        self.cbEndTime.setEnabled(OP)
        self.sbEndTime.setEnabled(OP)
        self.rbSeconds.setEnabled(OP)
        self.rbMinutes.setEnabled(OP)
        self.rbHours.setEnabled(OP)
        self.edtClientID.setEnabled(OP)
        self.cbLargeImage.setEnabled(OP)
        self.cbSmallImage.setEnabled(OP)
        self.edtDescription1.setEnabled(OP)
        self.edtDescription2.setEnabled(OP)
        self.cbButton1.setEnabled(OP)
        self.edtLabelButton1.setEnabled(OP)
        self.edtURLButton1.setEnabled(OP)
        self.cbButton2.setEnabled(OP)
        self.edtLabelButton2.setEnabled(OP)
        self.edtURLButton2.setEnabled(OP)

    def __checkRPC(self):
        COUNT = sqlite_query(DIR_APP, 'SELECT * FROM rpcsaved')
        if COUNT:
            self.__InEnableSaved(True)
        else:
            self.__InEnableSaved(False)

    def __loadRPC(self, idVuln):
        try:
            DATA_RPC = db_selectoneRPC(DIR_APP, idVuln)

            CLIENT_ID = str(DATA_RPC.get('idclient'))
            self.edtClientID.setText(CLIENT_ID)

            if CLIENT_ID:
                url = f"https://discordapp.com/api/oauth2/applications/{CLIENT_ID}/assets"
                _REQUEST = requests.get(url)

                self.cbLargeImage.addItem('')
                self.cbSmallImage.addItem('')
                for _XXX in _REQUEST.json():
                    self.cbLargeImage.addItem(_XXX.get('name'))
                    self.cbSmallImage.addItem(_XXX.get('name'))

            self.cbLargeImage.setCurrentText(DATA_RPC.get('largeimage'))
            self.cbSmallImage.setCurrentText(DATA_RPC.get('smallimage'))
            self.edtDescription1.setText(DATA_RPC.get('description1'))
            self.edtDescription2.setText(DATA_RPC.get('description2'))

            if DATA_RPC.get('starttime'):
                self.cbStartTime.setChecked(True)
            else:
                self.cbStartTime.setChecked(False)

            if DATA_RPC.get('endtime'):
                self.cbEndTime.setChecked(True)
            else:
                self.cbEndTime.setChecked(False)

            self.sbEndTime.setValue(DATA_RPC.get('endtimevalue'))
            
            if DATA_RPC.get('endtimetype') == 0:
                self.rbSeconds.setChecked(True)
            elif DATA_RPC.get('endtimetype') == 1:
                self.rbMinutes.setChecked(True)
            elif DATA_RPC.get('endtimetype') == 2:
                self.rbHours.setChecked(True)

            if DATA_RPC.get('button1'):
                self.cbButton1.setChecked(True)
            else:
                self.cbButton1.setChecked(False)

            self.edtLabelButton1.setText(DATA_RPC.get('button1name'))
            self.edtURLButton1.setText(DATA_RPC.get('button1url'))

            if DATA_RPC.get('button2'):
                self.cbButton2.setChecked(True)
            else:
                self.cbButton2.setChecked(False)

            self.edtLabelButton2.setText(DATA_RPC.get('button2name'))
            self.edtURLButton2.setText(DATA_RPC.get('button2url'))
        except:
            self.__resetRPC()

    def btnDeleteClicked(self):
        index=(self.twSaved.selectionModel().currentIndex())
        value_id = index.sibling(index.row(),0).data()
        __data = { 'id': value_id }

        reply = QMessageBox.question(self, '{0} ( {1} )'.format(APP_TITLE, APP_VERSION), "Do you really want to delete it?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            db_removeRPC(DIR_APP, __data)
            self.twSaved.removeRow(self.twSaved.currentRow())
            self.__checkRPC()

    def btnUpVulnerabilityClicked(self):
        row = self.twSaved.currentRow()
        column = self.twSaved.currentColumn();
        if row > 0:
            if row < self.twSaved.rowCount():
                index_sel = self.twSaved.selectionModel().currentIndex()
                inx_old = self.twSaved.currentRow() -1                          # row table
                id_old = index_sel.sibling(index_sel.row() -1,0).data()         # id
                myorder_old = index_sel.sibling(index_sel.row() -1,1).data()    # myorder

                inx_new = self.twSaved.currentRow()                             # row table
                id_new = index_sel.sibling(index_sel.row(),0).data()            # id
                myorder_new = index_sel.sibling(index_sel.row(),1).data()       # myorder

                value = { 'table': 'rpcsaved', 'idold': id_old, 'myorderold': myorder_old, 'idnew': id_new, 'myordernew': myorder_new }

                updown_data(DIR_APP, value)
                self.twSaved.setItem(inx_old, 1, QtWidgets.QTableWidgetItem('{0}'.format(myorder_new)))
                self.twSaved.setItem(inx_new, 1, QtWidgets.QTableWidgetItem('{0}'.format(myorder_old)))

            self.twSaved.insertRow(row-1)
            for i in range(self.twSaved.columnCount()):
               self.twSaved.setItem(row-1,i,self.twSaved.takeItem(row+1,i))
               self.twSaved.setCurrentCell(row-1,column)
            self.twSaved.removeRow(row+1)

    def btnDownVulnerabilityClicked(self):
        row = self.twSaved.currentRow()
        column = self.twSaved.currentColumn();
        if row < self.twSaved.rowCount()-1:
            if row >= 0:
                index_sel = self.twSaved.selectionModel().currentIndex()
                inx_old = self.twSaved.currentRow() +1                          # row table
                id_old = index_sel.sibling(index_sel.row() +1,0).data()         # id
                myorder_old = index_sel.sibling(index_sel.row() +1,1).data()    # myorder

                inx_new = self.twSaved.currentRow()                             # row table
                id_new = index_sel.sibling(index_sel.row(),0).data()            # id
                myorder_new = index_sel.sibling(index_sel.row(),1).data()       # myorder

                value = { 'table': 'rpcsaved', 'idold': id_old, 'myorderold': myorder_old, 'idnew': id_new, 'myordernew': myorder_new }

                updown_data(DIR_APP, value)
                self.twSaved.setItem(inx_old, 1, QtWidgets.QTableWidgetItem('{0}'.format(myorder_new)))
                self.twSaved.setItem(inx_new, 1, QtWidgets.QTableWidgetItem('{0}'.format(myorder_old)))

            self.twSaved.insertRow(row+2)
            for i in range(self.twSaved.columnCount()):
               self.twSaved.setItem(row+2,i,self.twSaved.takeItem(row,i))
               self.twSaved.setCurrentCell(row+2,column)
            self.twSaved.removeRow(row)


    def __save(self):
        index=(self.twSaved.selectionModel().currentIndex())
        value=index.sibling(index.row(),0).data()

        if self.rbSeconds.isChecked():
            ENDTIMETYPE = 0
        elif self.rbMinutes.isChecked():
            ENDTIMETYPE = 1
        elif self.rbHours.isChecked():
            ENDTIMETYPE = 2
        else:
            ENDTIMETYPE = 3

        RPC_DATA = {'id': value,
            'starttime': int(self.cbStartTime.isChecked()),
            'endtime':  int(self.cbEndTime.isChecked()),
            'endtimevalue':  self.sbEndTime.value(),
            'endtimetype': ENDTIMETYPE,
            'idclient': int(self.edtClientID.text()),
            'largeimage': self.cbLargeImage.currentText(),
            'largetext': '',
            'smallimage': self.cbSmallImage.currentText(),
            'smalltext': '',
            'description1': self.edtDescription1.text(),
            'description2': self.edtDescription2.text(),
            'button1': int(self.cbButton1.isChecked()),
            'button1name': self.edtLabelButton1.text(),
            'button1url': self.edtURLButton1.text(),
            'button2': int(self.cbButton2.isChecked()),
            'button2name': self.edtLabelButton2.text(),
            'button2url': self.edtURLButton2.text()}
        row, status = db_updateRPC(DIR_APP, RPC_DATA)
        self.__resetRPC()
        self.__loadRPC(row['id'])


    def __updateRPCDiscord(self):
        CLIENT_ID = self.edtClientID.text()
        DESCRIPTION1 = self.edtDescription1.text()
        DESCRIPTION2 = self.edtDescription2.text()
        if len(self.cbLargeImage.currentText()) > 1:
            LARGE_IMAGE = self.cbLargeImage.currentText()
        else:
            LARGE_IMAGE = None
        LARGE_TEXT = None
        if len(self.cbSmallImage.currentText()) > 1:
            SMALL_IMAGE = self.cbSmallImage.currentText()
        else:
            SMALL_IMAGE = None
        SMALL_TEXT = None
        RCP_SPEC = None
        RCP_JOIN = None
        RCP_TIME_START = None
        RCP_TIME_END = None
        BUTTONS = []
        if self.cbButton1.isChecked():
            BUTTONS.append({"label":self.edtLabelButton1.text(), "url":self.edtURLButton1.text()})
        
        if self.cbButton2.isChecked():
            BUTTONS.append({"label":self.edtLabelButton2.text(), "url":self.edtURLButton2.text()})
        
        if len(BUTTONS) == 0:
            BUTTONS = None
        
        if self.cbStartTime.isChecked():
            RCP_TIME_START = int(time.time())

        if self.rbSeconds.isChecked():
            ENDTIMETYPE = int(self.sbEndTime.value())
        elif self.rbMinutes.isChecked():
            ENDTIMETYPE = int(self.sbEndTime.value()) * 60
        elif self.rbHours.isChecked():
            ENDTIMETYPE = (int(self.sbEndTime.value()) * 60 ) * 60
        else:
            ENDTIMETYPE = ((int(self.sbEndTime.value()) * 60 ) * 60) * 60
        
        if self.cbStartTime.isChecked() and self.cbEndTime.isChecked():
            RCP_TIME_END = int(time.time()) + ENDTIMETYPE

        RPC.client_id = CLIENT_ID
        RPC.connect()
        RPC.update(
            large_image = LARGE_IMAGE,
            large_text = LARGE_TEXT,
            state = DESCRIPTION1,
            details = DESCRIPTION2,
            small_image = SMALL_IMAGE,
            small_text = SMALL_TEXT,
            start = RCP_TIME_START,
            end = RCP_TIME_END,
            spectate = RCP_SPEC,
            join = RCP_JOIN,
            buttons = BUTTONS
        )
    
    def btnURLDevClicked(self):
        process = QtCore.QProcess(self)
        process.start('xdg-open', ['https://discord.com/developers/applications'])

    def __connect(self):
        CLIENT_ID = self.edtClientID.text()
        if self.CONNECTED is False:
            if len(CLIENT_ID) > 5:
                try:
                    self.__save()
                    self.__updateRPCDiscord()
                    self.CONNECTED = True
                    ICON_ONLINE = icon_online(DIR_APP)
                    self.btnConnect.setIcon(ICON_ONLINE)
                    self.btnConnect.setToolTip("Disconnect RPC")
                    self.edtClientID.setEnabled(False)
                    self.btnDelete.setEnabled(False)
                    self.btnUp.setEnabled(False)
                    self.btnDown.setEnabled(False)
                    index=(self.twSaved.selectionModel().currentIndex())
                    self.CONNECTED_index = index.row()
                    value=index.sibling(index.row(),2).data()
                    self.twSaved.setItem(index.row(), 2, QtWidgets.QTableWidgetItem(ICON_ONLINE, value))
                except:
                    self.CONNECTED = False
                    ICON_OFFLINE = icon_offline(DIR_APP)
                    self.btnConnect.setIcon(ICON_OFFLINE)
                    self.btnConnect.setToolTip("Connect RPC")
                    self.edtClientID.setEnabled(True)
                    self.btnDelete.setEnabled(True)
                    self.btnUp.setEnabled(True)
                    self.btnDown.setEnabled(True)
                    self.__msg_error("Error connecting to the ID Client.")
                    if self.CONNECTED_index >= 0:
                        index=(self.twSaved.selectionModel().currentIndex())
                        value=index.sibling(self.CONNECTED_index,2).data()
                        self.twSaved.setItem(self.CONNECTED_index, 2, QtWidgets.QTableWidgetItem(ICON_OFFLINE, value))
            else:
                self.CONNECTED = False
                ICON_OFFLINE = icon_offline(DIR_APP)
                self.btnConnect.setIcon(ICON_OFFLINE)
                self.btnConnect.setToolTip("Connect RPC")
                self.edtClientID.setEnabled(True)
                self.btnDelete.setEnabled(True)
                self.btnUp.setEnabled(True)
                self.btnDown.setEnabled(True)
                self.__msg_error("Enter the correct Client ID!")
                if self.CONNECTED_index >= 0:
                    index=(self.twSaved.selectionModel().currentIndex())
                    value=index.sibling(self.CONNECTED_index,2).data()
                    self.twSaved.setItem(self.CONNECTED_index, 2, QtWidgets.QTableWidgetItem(ICON_OFFLINE, value))
        else:
            try:
                RPC.client_id = CLIENT_ID
                RPC.close()
                self.CONNECTED = False
                ICON_OFFLINE = icon_offline(DIR_APP)
                self.btnConnect.setIcon(ICON_OFFLINE)
                self.btnConnect.setToolTip("Connect RPC")
                self.edtClientID.setEnabled(True)
                self.btnDelete.setEnabled(True)
                self.btnUp.setEnabled(True)
                self.btnDown.setEnabled(True)
                if self.CONNECTED_index >= 0:
                    index=(self.twSaved.selectionModel().currentIndex())
                    value=index.sibling(self.CONNECTED_index,2).data()
                    self.twSaved.setItem(self.CONNECTED_index, 2, QtWidgets.QTableWidgetItem(ICON_OFFLINE, value))
            except:
                pass


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = frmMain()
    app.exec_()