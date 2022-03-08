import cv2
import numpy as np

from time import sleep
from PyQt5 import QtGui
from PyQt5 import QtCore

from time import sleep
from PyQt5 import QtGui
from PyQt5 import QtCore
from pdf2image import convert_from_path


class RenderQThread(QtCore.QObject):
    frame_signal = QtCore.pyqtSignal(QtGui.QImage)

    def __init__(
        self,
        file_list,
        default_fps=30.0,
        default_delay=10.0,
        default_transition_time=1.0,
    ):
        super().__init__()
        self.__pdf_ext = None
        self.__image_ext = None
        self.__video_ext = None
        self.__last_frame = None
        self.__file_list = file_list
        self.__frame_size = (1920, 1080)
        self.__default_fps = default_fps
        self.__default_delay = default_delay
        self.__default_transition_time = default_transition_time

    @property
    def pdf_ext(self):
        return self.__pdf_ext

    @pdf_ext.setter
    def pdf_ext(self, value):
        assert isinstance(value, (tuple, list))
        self.__pdf_ext = value

    @property
    def image_ext(self):
        return self.__image_ext

    @image_ext.setter
    def image_ext(self, value):
        assert isinstance(value, (tuple, list))
        self.__image_ext = value

    @property
    def video_ext(self):
        return self.__video_ext

    @video_ext.setter
    def video_ext(self, value):
        assert isinstance(value, (tuple, list))
        self.__video_ext = value

    @property
    def frame_size(self):
        return self.__frame_size

    @frame_size.setter
    def frame_size(self, value):
        assert isinstance(value, (tuple, list))
        self.__frame_size = value

    def process_pdf(self, file):
        images = convert_from_path(file)
        image = np.asanyarray(images[0])
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        image_qt = self.convert_to_qt(image)
        image_qt = self.resize_frame(image_qt)
        if self.__last_frame is None:
            self.render_frame(image_qt)
        else:
            image = self.transition_frame(image_qt)
        
        sleep(self.__default_delay)
        self.__last_frame = image

    def process_image(self, file):
        image = cv2.imread(file)
        image_qt = self.convert_to_qt(image)
        image_qt = self.resize_frame(image_qt)
        if self.__last_frame is None:
            self.render_frame(image_qt)
        else:
            image = self.transition_frame(image_qt)
        
        sleep(self.__default_delay)
        self.__last_frame = image

    def process_video(self, file):
        cap = cv2.VideoCapture(file)
        fps = cap.get(cv2.CAP_PROP_FPS)
        fps = fps if fps else self.__default_fps
        transitted = False
        while(cap.isOpened()):
            ret, frame = cap.read()
            if ret:
                frame_qt = self.convert_to_qt(frame)
                frame_qt = self.resize_frame(frame_qt)
                if self.__last_frame is None or transitted:
                    self.render_frame(frame_qt)
                    sleep(1 / fps)
                else:
                    _ = self.transit_frame(frame)
                    transitted = True
                
            else:
                break
        
        self.__last_frame = self.convert_to_numpy(frame_qt)
        cap.release()
        
    def convert_to_qt(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qt_frame = QtGui.QImage(frame.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        return qt_frame
    
    def resize_frame(self, frame):
        qt_image = frame.scaled(self.__frame_size[0], self.__frame_size[1], QtCore.Qt.KeepAspectRatio)
        return qt_image
    
    def convert_to_numpy(self, frame):
        frame = frame.convertToFormat(QtGui.QImage.Format_RGB32)

        width = frame.width()
        height = frame.height()

        bits = frame.bits()
        bits.setsize(frame.byteCount())
        image = np.array(bits).reshape(height, width, 3)
        return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    
    def transit_frame(self, frame_qt):
        frame = self.convert_to_numpy(frame_qt)
        for idx in np.linspace(0, 1, self.__default_transition_time * 1000):
            alpha = idx
            be
        

    def render_frame(self, qt_image):
        self.frame_signal.emit(qt_image)

    def run(self):
        for file in self.__file_list:
            ext = self.__file.split(".")[-1]
            if ext in self.pdf_ext:
                self.process_pdf(file)
            elif ext in self.image_ext:
                self.process_image(file)
            elif ext in self.video_ext:
                self.process_video(file)
            else:
                raise ValueError("Unknown file type: {}".format(ext))
