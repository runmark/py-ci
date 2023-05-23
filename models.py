import datetime


class Project:
    def __init__(self, config=None):
        self.config = config
        self.current_commit = None
        self.pending_commit = None
        self.processing = False
        self.build_results = []

    @property
    def id(self) -> str:
        return self.config["id"]

    def end_build(self, result):
        self.current_commit = self.pending_commit
        self.pending_commit = None
        self.processing = False
        self.build_results.append(result)


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

    def fail(self, e: Exception):
        self.success = False
        self.error = str(e)

    def finish(self):
        self.end_time = datetime.now()


class TaskResult:
    def __init__(self, fmt=None, content=None):
        self.success = True
        self.type = None
        self.format = fmt
        self.content = content


class Database:
    def __init__(self, config):
        self.projects = [Project(x) for x in config["projects"]]

    def find_project(self, project_id: str):
        return [p for p in self.projects if p.id == project_id]


class LintIssue:
    def __init__(self, filename, line, column, name, description):
        self.filename = filename
        self.line = line
        self.column = column
        self.name = name
        self.description = description


class UnitTestResult:
    def __init__(self):
        self.pass_count = 0
        self.fail_count = 0
        self.error_count = 0
