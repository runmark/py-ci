from threading import Thread
import multiprocessing as mp


class Agent:
    def __init__(self, config):
        self.config = config
        self.project_queue = mp.Queue()
        self.result_queue = mp.Queue()
