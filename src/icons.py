from PyQt5 import (QtGui, QtCore)
from PyQt5.QtCore import (Qt)
from PyQt5.QtGui import (QPixmap, QIcon, QColor, QPainter, QPen, QBrush)

def icon_app(DIR_APP):
    return QtGui.QIcon('{0}/icons/rpcdiscord.png'.format(DIR_APP))

def icon_save(DIR_APP):
    return QtGui.QIcon('{0}/icons/save.svg'.format(DIR_APP))

def icon_trash(DIR_APP):
    return QtGui.QIcon('{0}/icons/trash.svg'.format(DIR_APP))

def icon_info(DIR_APP):
    return QtGui.QIcon('{0}/icons/info.svg'.format(DIR_APP))

def icon_git(DIR_APP):
    return QtGui.QIcon('{0}/icons/git.svg'.format(DIR_APP))

def icon_question(DIR_APP):
    return QtGui.QIcon('{0}/icons/question.svg'.format(DIR_APP))

def icon_qt(DIR_APP):
    return QtGui.QIcon('{0}/icons/qt.svg'.format(DIR_APP))

def icon_close(DIR_APP):
    return QtGui.QIcon('{0}/icons/close.svg'.format(DIR_APP))

def icon_quit(DIR_APP):
    return QtGui.QIcon('{0}/icons/sign-out.svg'.format(DIR_APP))

def icon_plus(DIR_APP):
    return QtGui.QIcon('{0}/icons/plus.svg'.format(DIR_APP))

def icon_up(DIR_APP):
    return QtGui.QIcon('{0}/icons/up.svg'.format(DIR_APP))
    
def icon_down(DIR_APP):
    return QtGui.QIcon('{0}/icons/down.svg'.format(DIR_APP))

def icon_update(DIR_APP):
    return QtGui.QIcon('{0}/icons/refresh.svg'.format(DIR_APP))

def icon_none(DIR_APP):
    return QtGui.QIcon('{0}/icons/none.png'.format(DIR_APP))

def icon_online(DIR_APP):
    return QtGui.QIcon('{0}/icons/online.png'.format(DIR_APP))

def icon_offline(DIR_APP):
    return QtGui.QIcon('{0}/icons/offline.png'.format(DIR_APP))

def icon_link(DIR_APP):
    return QtGui.QIcon('{0}/icons/globe-americas.svg'.format(DIR_APP))
