import datetime


class Project:
    def __init__(self, config=None):
        self.config = config
        self.current_commit = None
        self.pending_commit = None
        self.processing = False
        self.build_results = []


class BuildResult:
    def __init__(self):
        self.project_id = None
        self.commit_id = None
        self.agent_id = None
        self.success = True
        self.error = None
        self.start_time = datetime.now()
        self.end_time = None
        self.tasks = []


class TaskResult:
    def __init__(self, fmt=None, content=None):
        self.success = True
        self.type = type
        self.format = fmt
        self.content = content


class Database:
    def __init__(self, config):
        self.projects = [Project(x) for x in config["projects"]]
