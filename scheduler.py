import queue
import random
from threading import Thread

from agent import Agent
from models import BuildResult, Project

import multiprocessing as mp
import vcs


class Scheduler(Thread):
    def __init__(self, config, db):
        super().__init__()
        self._config = config
        self.db = db
        self.agents = [self.start_agent(c) for c in config["agents"]]

    def start_agent(self, config):
        agent = Agent(config)
        p = mp.Process(target=agent, daemon=True)
        p.start()
        return agent

    def detect_change(self, project: Project):
        if project.processing:
            return
        commit_id = vcs.get_last_commit_id(project.config["url"])
        if commit_id != project.current_commit:
            project.pending_commit = commit_id
            agent: Agent = self.choose_agent(project)
            agent.schedule(project)

    def detect_result(self, agent: Agent):
        # if len(agent.result_queue) == 0:
        #     return
        try:
            result: BuildResult = agent.result_queue.get(block=False, timeout=None)
            print(f"{agent.id} got build result: {result}")
            result.agent_id = agent.id
            project = self.db.find_project(result.project_id)
            project.end_build(result)
            print(f"Project {project.id} end build, commit={project.current_commit}")
        except queue.Empty:
            pass

    def choose_agent(self, project: Project):
        return random.choice(self.agents)
