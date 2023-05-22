import os
import shutil
import subprocess
from threading import Thread
import multiprocessing as mp
import traceback
import uuid

from models import BuildResult, Project, TaskResult
import vcs


class Agent:
    def __init__(self, config):
        self.config = config
        self.project_queue = mp.Queue()
        self.result_queue = mp.Queue()

    @property
    def id(self):
        return self.config["id"]

    def schedule(self, project: Project):
        project.processing = True
        self.result_queue.put(project)
        print(
            f"Project {project.id} with commit {project.pending_commit} scheduled to {self.id}"
        )

    def __call__(self, *args, **kwargs):
        while True:
            project = self.result_queue.get()
            builder = ProjectBuilder(self, project)
            builder.start()


class ProjectBuilder(Thread):
    def __init__(self, agent: Agent, project: Project):
        super().__init__()
        self.agent = agent
        self.project = project

        self.work_dir = None
        self.venv_name = "venv"

        self.result = BuildResult()
        self.result.project_id = project.id
        self.result.commit_id = project.pending_commit
        self.result.agent_id = agent.id

    def run(self):
        self.work_dir = os.path.join(self.agent.workDir(), uuid.uuid4().hex)
        try:
            vcs.clone(
                self.project.config["url"],
                self.work_dir,
                commit_id=self.project.pending_commit,
            )
            for task_config in self.project["tasks"]:
                self.run_task(task_config)
        except Exception as e:
            self.result.fail(e)
            traceback.print_exc()
        finally:
            self.result.finish()
            shutil.rmtree(self.work_dir)
            self.agent.result_queue.put(self.result)

    def run_task(self, config: dict):
        runner_type = {
            "venv": run_venv,
            "pylint": run_pylint,
            "unittest": run_unittest,
        }

        task_type = config["type"]
        assert task_type in runner_type, f"Unsupported task type: {task_type}"

        runner = runner_type[task_type]
        result = runner(self, config)
        if result:
            result.type = task_type
            self.result.tasks.append(result)

    def run_cmd(self, cmd: str) -> str:
        p = subprocess.run(
            cmd,
            shell=True,
            cwd=self.work_dir,
            capture_output=True,
        )

        if p.stdout:
            return p.stdout.decode("UTF-8")


def run_venv(builder, config: dict) -> TaskResult:
    venv_name, packages_file = config["name"], config["packages-file"]
    builder.venv_name = venv_name
    builder.run_cmd(f"python3 -m venv {venv_name}")
    builder.run_cmd(f"{venv_name}/bin/pip install -r {packages_file}")


def run_pylint(builder, config: dict) -> TaskResult:
    venv_name, pattern = builder.venv_name, config["pattern"]
    output = builder.run_cmd(f"{venv_name}/bin/pylint {pattern}")
    return TaskResult("pylint", output)


def run_unittest(builder, config: dict) -> TaskResult:
    venv_name, params = builder.venv_name, config["params"]
    output = builder.run_cmd(f"{venv_name}/bin/python -m unittest {params} 2>&1")
    return TaskResult("unittest", output)
