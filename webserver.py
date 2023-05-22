from threading import Thread


class WebServer(Thread):
    def __init__(self, db):
        super().__init__()
        self._db = db
