import os
import sys
import yaml
import argparse

from glob import glob

from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets

from utils import VideoQThread
from utils import ImageQThread
from utils import YAML2argparse

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    
parser = argparse.ArgumentParser()
parser.add_argument("--config", type=str, help="Path to config file")


class App(QtWidgets.QWidget):
    def __init__(self, args):
        super().__init__()
        self.__idx = 0
        self.__args = args
        self.__key_ctrl = False
        self.__thread = QtCore.QThread()
        self.__video_thread = VideoQThread(args.video_fps)
        self.__image_thread = ImageQThread(args.image_delay)
        
        self.__file_list = glob(os.path.join(args.directory, "*"))
        self.__file = self.__file_list[0]
        
        self.init_ui()
        self.__transition = False
        self.__effect = QtWidgets.QGraphicsOpacityEffect()
        self.main_frame.setGraphicsEffect(self.__effect)
        
        self.run()
        
    def init_ui(self):
        self.resize(
            self.__args.resolution[0],
            self.__args.resolution[1]
        )
        # self.showFullScreen()
        
        self.main_frame = QtWidgets.QLabel(self)
        self.main_frame.resize(
            self.__args.resolution[0],
            self.__args.resolution[1]
        )
        self.main_frame.setAlignment(QtCore.Qt.AlignCenter)
        
        self.__image_thread.frame_size = (
            self.__args.resolution[0],
            self.__args.resolution[1]
        )
        self.__video_thread.frame_size = (
            self.__args.resolution[0],
            self.__args.resolution[1]
        )
        
        self.showFullScreen()
        
    def run(self):
        ext = self.__file.split(".")[-1]
        if ext in self.__args.image_ext:
            self.worker = self.__image_thread
        else:
            self.worker = self.__video_thread

        self.worker.file = self.__file
        self.worker.frame_signal.connect(self.update_frame)
        self.worker.moveToThread(self.__thread)
        self.__thread.started.connect(self.worker.run)

        self.worker.done_signal.connect(self.next_file)
        self.__thread.start()
        self.show()
        
    def next_file(self):
        # self.fade_out()
        self.__thread.quit()
        
        self.__idx += 1
        if self.__idx == len(self.__file_list):
            self.__idx = 0
        
        print(self.__idx)
        self.__file = self.__file_list[self.__idx]
        self.run()
        
    def fade_in(self):
        self.animation = QtCore.QPropertyAnimation(self.__effect, b"opacity")
        self.animation.setDuration(1000)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()
        
    def fade_out(self):
        self.animation = QtCore.QPropertyAnimation(self.__effect, b"opacity")
        self.animation.setDuration(1000)
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.start()
        
    @QtCore.pyqtSlot(QtGui.QImage)
    def update_frame(self, image):
        self.main_frame.setPixmap(QtGui.QPixmap.fromImage(image))
        # self.fade_in()
        
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Control:
            self.__key_ctrl = True
            
    def keyReleaseEvent(self, event):
        if event.key() == QtCore.Qt.Key_Control:
            self.__key_ctrl = False
            
        if event.key() == QtCore.Qt.Key_Q:
            if self.__key_ctrl:
                self.close()


if __name__ == "__main__":
    args = parser.parse_args()
        
    YAML2argparse.parse_yaml(args.config, args)

    app = QtWidgets.QApplication(sys.argv)
    ex = App(args)
    sys.exit(app.exec_())
