from urllib import error
from urllib import request


class NetworkChecker:
    def __init__(self, remote_url):
        self.__remote_url =remote_url

    def check(self):
        try:
            request.urlopen(self.__remote_url, timeout=1)
            return True
        except error.URLError as err:
            return False
