import cv2
import numpy as np

from math import ceil
from math import floor
from time import sleep
from PyQt5 import QtGui
from PyQt5 import QtCore
from collections import deque
from pdf2image import convert_from_path


class RenderQThread(QtCore.QObject):
    frame_signal = QtCore.pyqtSignal(QtGui.QImage)

    def __init__(
        self,
        file_list=None,
        default_fps=30.0,
        default_delay=10.0,
        start_running=False,
        default_transition_time=1.0,
    ):
        super().__init__()
        self.__pdf_ext = None
        self.__image_ext = None
        self.__video_ext = None
        self.__last_frame = None
        self.__file_list = file_list
        self.__running = start_running
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
        
    def pad_to_size(self, image):
        image_height, image_width , _ = image.shape
        aspect_ratio = image_width / image_height
        frame_ratio = self.frame_size[0] / self.frame_size[1]
        if aspect_ratio > frame_ratio:
            diff = self.frame_size[1] - image_height
            top, bottom = ceil(diff / 2), floor(diff / 2)
            left, right = 0, 0
        elif aspect_ratio < frame_ratio:
            diff = self.frame_size[0] - image_width
            top, bottom = 0, 0
            left, right = ceil(diff / 2), floor(diff / 2)
        else:
            return image
        
        return cv2.copyMakeBorder(image, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(255, 255, 255))
        
    def resize_frame(self, image):
        image_height, image_width , _ = image.shape
        aspect_ratio = image_width / image_height
        frame_ratio = self.frame_size[0] / self.frame_size[1]
        if aspect_ratio > frame_ratio:
            new_width = self.frame_size[0]
            new_height = int(new_width / aspect_ratio)
            diff = image_width - new_width
        elif aspect_ratio < frame_ratio:
            new_height = self.frame_size[1]
            new_width = int(new_height * aspect_ratio)
            diff = image_height - new_height
        else:
            new_width = self.frame_size[0]
            new_height = self.frame_size[1]
            diff = image_width - new_width
        
        if diff > 0:
            interpolation = cv2.INTER_AREA
        elif diff < 0:
            interpolation = cv2.INTER_CUBIC
        else:
            return image
        
        return cv2.resize(image, (new_width, new_height), interpolation=interpolation)
        
    def convert_to_qt(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qt_frame = QtGui.QImage(frame.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        return qt_frame
    
    def convert_to_numpy(self, frame):
        frame = frame.convertToFormat(QtGui.QImage.Format_RGB32)

        width = frame.width()
        height = frame.height()

        bits = frame.bits()
        bits.setsize(frame.byteCount())
        image = np.array(bits).reshape(height, width, 4)
        return image[:, :, :3]
    
    def transit_frame(self, frame_qt):
        frame_1 = self.convert_to_numpy(frame_qt)
        frame_2 = self.__last_frame
        for idx in np.linspace(0, 1, int(self.__default_transition_time * 100)):
            alpha = idx
            beta = 1 - alpha
            out_frame = cv2.addWeighted(frame_1, alpha, frame_2, beta, 0)
            out_qt = self.convert_to_qt(out_frame)
            self.render_frame(out_qt)
            sleep(self.__default_transition_time / 500)
        
        return frame_1

    def render_frame(self, qt_image):
        self.frame_signal.emit(qt_image)

    def process_pdf(self, file):
        images = convert_from_path(file)
        image = np.asanyarray(images[0])
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        image = self.resize_frame(image)
        image = self.pad_to_size(image)
        image_qt = self.convert_to_qt(image)
        if self.__last_frame is None:
            self.render_frame(image_qt)
        else:
            image = self.transit_frame(image_qt)
        
        sleep(self.__default_delay)
        self.__last_frame = image

    def process_image(self, file):
        image = cv2.imread(file)
        image = self.resize_frame(image)
        image = self.pad_to_size(image)
        image_qt = self.convert_to_qt(image)
        if self.__last_frame is None:
            self.render_frame(image_qt)
        else:
            image = self.transit_frame(image_qt)
        
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
                frame = self.resize_frame(frame)
                frame = self.pad_to_size(frame)
                frame_qt = self.convert_to_qt(frame)
                if self.__last_frame is None or transitted:
                    self.render_frame(frame_qt)
                else:
                    _ = self.transit_frame(frame_qt)
                    transitted = True
                
                sleep(1 / fps)
            else:
                break
        
        self.__last_frame = self.convert_to_numpy(frame_qt)
        cap.release()
        
    @QtCore.pyqtSlot()
    def pause_render(self):
        self.__running = False
    
    @QtCore.pyqtSlot(list)
    def resume_render(self, file_list):
        self.__file_list = deque(file_list)
        self.__running = True

    def run(self):
        while True:
            if not self.__running:
                continue

            file = self.__file_list[0]
            ext = file.split(".")[-1]
            if ext in self.pdf_ext:
                self.process_pdf(file)
            elif ext in self.image_ext:
                self.process_image(file)
            elif ext in self.video_ext:
                self.process_video(file)
            else:
                raise ValueError("Unknown file type: {}".format(ext))
            
            self.__file_list.rotate(-1)
