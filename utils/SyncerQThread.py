import os
import yaml
import socket
import imohash

from time import sleep
from shutil import move
from PyQt5 import QtCore
from tempfile import TemporaryDirectory
from smb.SMBConnection import SMBConnection


default_file = {
    "hash"
    "last_modified": 0.0,
    "local_path": None
}


class SyncerQThread(QtCore.QObject):
    pause_signal = QtCore.pyqtSignal()
    resume_signal = QtCore.pyqtSignal()

    def __init__(self, local_folder, network_config, hashes_file=None):
        super().__init__()
        self.__local_folder = local_folder
        smb_server, smb_share, *smb_folder = list(filter(None, network_config["folder"].split("/")))
        self.__smb_share = smb_share
        self.__smb_folder = "/".join(smb_folder)
        
        self.__conn = SMBConnection(network_config["login"], network_config["password"], socket.gethostname(), network_config["name"])
        self.__conn.connect(smb_server, 445)
        
        self.__temp_folder = None

        if hashes_file is None:
            hashes_file = os.path.join(local_folder, ".hashes")
            
        self.__hashes_file = hashes_file

        with open(hashes_file, "w+") as _file:
            hashes = yaml.safe_load(_file)
            
        self.__hashes = hashes if hashes is not None else {}
        
    @property
    def hashes(self):
        return self.__hashes
            
    def check_file_condition(self, last_modified, local_file):

        if last_modified > local_file["last_modified"]:
            return True
        
        return False
            
    def download_file(self, file):
        if self.__temp_folder is None:
            self.__temp_folder = TemporaryDirectory()
            
        temp_dir = self.__temp_folder.name
        temp_file = os.path.join(temp_dir, file.filename)
        self.__conn.retrieveFile(
            self.__smb_share,
            os.path.join(self.__smb_folder, file.filename),
            open(temp_file, "wb")
        )
        return temp_file
            
    def run(self):
        while True:
            network_files = self.__conn.listPath(self.__smb_share, self.__smb_folder)
            network_files = [file for file in network_files if file.filename not in ['.', '..']]
            temp_files = []
            for file in network_files:
                local_file = self.__hashes.get(file.filename, default_file)
                last_modified = file.create_time if file.create_time > file.last_write_time else file.last_write_time
                if not self.check_file_condition(last_modified, local_file):
                    continue
                
                temp_file = self.download_file(file)
                temp_hash = imohash.hashfile(temp_file)
                
                if temp_hash == local_file["hash"]:
                    os.remove(temp_file)
                    continue
                
                temp_files.append((file.filename, temp_file, temp_hash, last_modified))
                
            if temp_files:
                self.pause_signal.emit()
                for filename, file, hash, last_modified in temp_files:
                    move(file, self.__local_folder)
                    self.__hashes[filename] = {
                        "hash": hash,
                        "last_modified": last_modified,
                        "local_path": os.path.join(self.__local_folder, filename)
                    }
                
                with open(self.__hashes_file, "w+") as _file:
                    yaml.safe_dump(self.__hashes, _file)
                
                self.resume_signal.emit()
                
            sleep(300)