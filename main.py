import os
import sys
import argparse

from glob import glob

from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets

from utils import SyncerQThread
from utils import RenderQThread
from utils import YAML2argparse

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    
parser = argparse.ArgumentParser()
parser.add_argument("--config", type=str, help="Path to config file")
parser.add_argument("--network_config", type=str, help="Path to network config file", default=None)


class App(QtWidgets.QWidget):

    def __init__(self, args, network_args):
        super().__init__()
        self.__args = args
        self.__key_ctrl = False
        self.__thread_1 = QtCore.QThread()
        self.__thread_2 = QtCore.QThread()
        
        self.init_ui()

        if args.network_config is None:
            file_list = glob(
                os.path.join(
                    args.directory,
                    "*"
                )
            )
            self.__render_thread = RenderQThread(
                start_running=True,
                file_list=file_list,
                default_fps=args.video_fps,
                default_delay=args.image_delay,
                default_transition_time=args.transition_delay
            )
        else:
            self.__render_thread = RenderQThread(
                default_fps=args.video_fps,
                default_delay=args.image_delay,
                default_transition_time=args.transition_delay
            )
            self.__syncer_thread = SyncerQThread(args.directory, network_args)
            self.__syncer_thread.pause_signal.connect(self.__render_thread.pause_render)
            self.__syncer_thread.resume_signal.connect(self.__render_thread.resume_render)
            self.run_syncer()
        
        self.__render_thread.pdf_ext = args.pdf_ext
        self.__render_thread.image_ext = args.image_ext
        self.__render_thread.video_ext = args.video_ext
        self.__render_thread.frame_size = args.resolution

        self.__render_thread.frame_signal.connect(self.update_frame)
        
        self.run_render()
        
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
        
    def run_syncer(self):
        self.__syncer_thread.moveToThread(self.__thread_2)
        self.__thread_2.started.connect(self.__syncer_thread.run)
        self.__thread_2.start()
        
    def run_render(self):
        self.__render_thread.moveToThread(self.__thread_1)
        self.__thread_1.started.connect(self.__render_thread.run)
        self.__thread_1.start()
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
                self.__thread_1.quit()
                self.close()


if __name__ == "__main__":
    args = parser.parse_args()
    YAML2argparse.parse_yaml(args.config, args)
    
    network_args = parser.parse_args("")
    YAML2argparse.parse_yaml(args.network_config, network_args)

    app = QtWidgets.QApplication(sys.argv)
    ex = App(args, network_args)
    sys.exit(app.exec_())
