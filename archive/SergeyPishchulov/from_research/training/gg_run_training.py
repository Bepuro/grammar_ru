from tg.common import DataBundle
from tg.common.ml.batched_training import IndexedDataBundle

from tg.common.ml import batched_training as bt
from tg.common.ml.batched_training import torch as btt
from tg.common.ml.batched_training import context as btc
from yo_fluq_ds import fluq


from tg.grammar_ru.ml.components.attention_network import AttentionNetwork
from tg.common.ml.batched_training.torch.networks.lstm_network import LSTMFinalizer

from tg.grammar_ru.ml.components.extractor_settings import CoreExtractor
import datetime
from tg.grammar_ru.ml.components.training_task_factory import TaskFactory
from tg.grammar_ru.ml.components.training_task_factory import Conventions

from tg.grammar_ru.ml.components.yandex_delivery.training_job import TrainingJob
from tg.grammar_ru.ml.components.yandex_storage.s3_yandex_helpers import S3YandexHandler
from tg.common.delivery.jobs import SSHDockerJobRoutine, DockerOptions
from tg.common.delivery.packaging import FakeContainerHandler

from typing import Dict, Optional  # TODO delete redundant
from tg.common.delivery.training.architecture import FileCacheTrainingEnvironment
from tg.grammar_ru.ml.components.yandex_delivery.docker_tools import deploy_container
from tg.common.delivery.jobs.ssh_docker_job_routine import build_container
import torch
from pathlib import Path
from dotenv import load_dotenv
from tg.grammar_ru.ml.tasks.grammatical_gender.deliverable_stuff import ClassificationTask, ClassificationTaskByBatchSize
from tg.grammar_ru.common import Loc

load_dotenv(Loc.root_path / 'environment.env')

project_name = 'gg_project'
dataset_name = 'gg_lenta_big3featdist'
bucket = 'ggbucket'
task_name = f"task_{dataset_name}_120ep"

# def get_tasks():
#     tasks = []
#     for bs in [22000, 25000, 28000, 30000, 32000, 35000]:
#         task = ClassificationTaskByBatchSize(bs)
#         task.info["dataset"] = dataset_name
#         # "gg_task_lenta_full_20K_100ep"
#         task.info["name"] = f"task_{dataset_name}_{bs}_1ep"
#         tasks.append(task)
#     return tasks


# def get_training_job_with_many_tasks() -> TrainingJob:
#     tasks = get_tasks()
#     job = TrainingJob(
#         tasks=tasks,
#         project_name=project_name,
#         bucket=bucket
#     )
#     return job


def get_training_job() -> TrainingJob:
    task = ClassificationTask()
    task.info["dataset"] = dataset_name
    task.info["name"] = task_name

    job = TrainingJob(
        tasks=[task],
        project_name=project_name,
        bucket=bucket
    )
    return job


job = get_training_job()
# job_many_tasks = get_training_job_with_many_tasks()
# job = job_many_tasks
routine = SSHDockerJobRoutine(
    job=job,
    remote_host_address=None,
    remote_host_user=None,
    handler_factory=FakeContainerHandler.Factory(),
    options=DockerOptions(propagate_environmental_variables=["AWS_ACCESS_KEY_ID",
                                                             "AWS_SECRET_ACCESS_KEY"])
)
tag = 'v_' + datetime.datetime.now().time().strftime("%H_%M_%S")
dockerhub_repo = 'grammar_repo'  # name of your repo
dockerhub_login = 'sergio0x0'  # your login

local_img = 'gg_img'


# job.run()
# exit()
# b_path = Loc.bundles_path/'grammatical_gender/toy'
# data = DataBundle.load(b_path)

# task = ClassificationTask()
# task.create_task(data)
# temp_batch = task.task.generate_sample_batch(data,0)


# task = job.tasks[0]

# task.name = 'gg'
# model_folder = Path.home() / 'models' / f'{task.name}'
# env = FileCacheTrainingEnvironment(model_folder)
# # print(data)
# success = task.run_with_environment(data, env)
# task.in
# object_methods = [method_name for method_name in dir(task.task)
#                   if callable(getattr(task.task, method_name))]

# print(object_methods)

# 6a
# routine.local.execute()

# 6b
build_container(job, 'gg', '1', local_img,
                image_tag=tag)
deploy_container(local_img, dockerhub_repo, dockerhub_login, tag)
print(tag)
