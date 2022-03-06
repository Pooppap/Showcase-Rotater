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
        self.__args = args
        self.__key_ctrl = False
        self.thread = QtCore.QThread()
        self.image_thread = ImageQThread(args.image_delay)
        self.video_thread = VideoQThread(args.video_fps)
        
        self.__file_list = glob(os.path.join(args.directory, "*"))
        
        self.init_ui()
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
        
        self.image_thread.frame_size = (
            self.__args.resolution[0],
            self.__args.resolution[1]
        )
        self.video_thread.frame_size = (
            self.__args.resolution[0],
            self.__args.resolution[1]
        )
        
        self.showFullScreen()
        
    def run(self):
        for file in self.__file_list:
            ext = file.split(".")[-1]
            if ext in self.__args.image_ext:
                self.worker = self.image_thread
                self.image_thread.frame_signal.connect(self.update_frame)
                self.image_thread.moveToThread(self.thread)
                self.thread.started.connect(self.image_thread.run)
            else:
                self.worker = self.video_thread
                self.video_thread.frame_signal.connect(self.update_frame)
                self.video_thread.moveToThread(self.thread)
                self.thread.started.connect(self.video_thread.run)

        self.finished.connect(self.stop_thread)
        self.thread.start()
        self.show()
        
    def stop_thread(self):
        self.worker.stop()
        self.thread.quit()
        self.thread.wait()
        
    @QtCore.pyqtSlot(QtGui.QImage)
    def update_frame(self, image):
        self.main_frame.setPixmap(QtGui.QPixmap.fromImage(image))
        
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
    with open(args.config, "r") as _file:
        config = yaml.safe_load(_file)
        
    YAML2argparse.parse_yaml(config, args)

    app = QtWidgets.QApplication(sys.argv)
    ex = App(args)
    sys.exit(app.exec_())
