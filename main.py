import os
import sys
import argparse

from glob import glob

from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets

from utils import RenderQThread
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
        self.__thread = QtCore.QThread()
        
        file_list = glob(
            os.path.join(
                args.directory,
                "*"
            )
        )
        self.__render_thread = RenderQThread(
            file_list,
            args.video_fps,
            args.image_delay,
            args.transition_delay
        )
        self.__render_thread.pdf_ext = args.pdf_ext
        self.__render_thread.image_ext = args.image_ext
        self.__render_thread.video_ext = args.video_ext
        self.__render_thread.frame_size = args.resolution
        
        self.init_ui()
        
        self.run()
        
    def init_ui(self):
        self.resize(
            self.__args.resolution[0],
            self.__args.resolution[1]
        )
        
        self.main_frame = QtWidgets.QLabel(self)
        self.main_frame.resize(
            self.__args.resolution[0],
            self.__args.resolution[1]
        )
        self.main_frame.setAlignment(QtCore.Qt.AlignCenter)
        
        self.showFullScreen()
        
    def run(self):
        self.__render_thread.frame_signal.connect(self.update_frame)
        self.__render_thread.moveToThread(self.__thread)
        self.__thread.started.connect(self.__render_thread.run)

        self.__thread.start()
        self.show()
        
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
                self.__thread.quit()
                self.close()


if __name__ == "__main__":
    args = parser.parse_args()
    YAML2argparse.parse_yaml(args.config, args)

    app = QtWidgets.QApplication(sys.argv)
    ex = App(args)
    sys.exit(app.exec_())
