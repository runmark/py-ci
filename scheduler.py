from threading import Thread

from agent import Agent


class Scheduler(Thread):
    def __init__(self, config, db):
        super().__init__()
        self._config = config
        self._db = db
        self.agents = [Agent(c) for c in config["agents"]]
