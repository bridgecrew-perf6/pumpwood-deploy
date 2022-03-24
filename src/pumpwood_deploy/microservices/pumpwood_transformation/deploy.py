"""PumpWood DataLake Microservice Deploy."""
import os
import base64
from jinja2 import Template
from pumpwood_deploy.microservices.postgres.postgres import \
    create_ssl_key_ssl_crt
from typing import List
from .resources.resources_yml import (
    deployment_postgres, secrets, services__load_balancer,
    transformation_deployment, transformation_worker_estimation,
    transformation_worker_prediction, volume_postgres, test_postgres)


class PumpWoodTransformationMicroservice:
    """PumpWoodTransformationMicroservice."""

    def __init__(self, db_password: str, microservice_password: str,
                 bucket_name: str, version_app: str,
                 disk_name: str = None, disk_size: str = None,
                 postgres_public_ip: str = None,
                 repository: str = "gcr.io/repositorio-geral-170012",
                 firewall_ips: List[str] = None,
                 workers_timeout: int = 300, replicas: int = 1,
                 test_db_version: str = None,
                 test_db_repository: str = "gcr.io/repositorio-geral-170012",
                 debug: str = "FALSE"):
        """
        __init__: Class constructor.

        Args:
          db_password (str): password at database.
          microservice_password (str): Microservice password.
          disk_size (str): Disk size (ex.: 50Gi, 100Gi)
          disk_name (str): Name of the disk that will be used in postgres
          postgres_public_ip (str): Postgres public IP.
          bucket_name (str): Name of the bucket (Storage)
          version_app (str): App version.
          version_rawdata (str): Version of the raw data worker.
          version_dataloader (str): Version of the raw data worker.

        Kwargs:
          firewall_ips (list[str]): List with the IPs to allow connection to
            database.
          repository (str): Repository to pull Image.
          workers_timeout (int): Time in seconds to timeout of uwsgi worker.

        Returns:
          PumpWoodDatalakeMicroservice: New Object

        Raises:
          No especific raises.

        Example:
          No example yet.
        """
        disk_deploy = (disk_name is not None and disk_size is not None)
        if disk_deploy and test_db_version is not None:
            raise Exception(
                "When working with test database, disk is not used.")

        postgres_certificates = create_ssl_key_ssl_crt()
        self._db_password = base64.b64encode(db_password.encode()).decode()
        self._microservice_password = base64.b64encode(
            microservice_password.encode()).decode()

        self._ssl_crt = base64.b64encode(
            postgres_certificates['ssl_crt'].encode()).decode()
        self._ssl_key = base64.b64encode(
            postgres_certificates['ssl_key'].encode()).decode()

        self.postgres_public_ip = postgres_public_ip
        self.firewall_ips = firewall_ips

        self.debug = debug
        self.bucket_name = bucket_name
        self.disk_size = disk_size
        self.disk_name = disk_name
        self.base_path = os.path.dirname(__file__)

        self.workers_timeout = workers_timeout
        self.repository = repository
        self.version_app = version_app
        self.replicas = replicas

        self.test_db_version = test_db_version
        self.test_db_repository = test_db_repository

    def create_deployment_file(self):
        """create_deployment_file."""
        secrets_text_formated = secrets.format(
            db_password=self._db_password,
            microservice_password=self._microservice_password,
            ssl_key=self._ssl_key,
            ssl_crt=self._ssl_crt)

        volume_postgres_text_formated = volume_postgres.format(
            disk_size=self.disk_size,
            disk_name=self.disk_name)

        volume_postgres_text_f = None
        if self.test_db_version is not None:
            deployment_postgres_text_f = test_postgres.format(
                repository=self.test_db_repository,
                version=self.test_db_version)
        else:
            volume_postgres_text_f = volume_postgres.format(
                disk_size=self.disk_size,
                disk_name=self.disk_name)
            deployment_postgres_text_f = deployment_postgres

        transformation_deployment_formated = \
            transformation_deployment.format(
                repository=self.repository,
                version=self.version_app,
                bucket_name=self.bucket_name,
                workers_timeout=self.workers_timeout,
                replicas=self.replicas,
                debug=self.debug)
        worker_estimation_formated = transformation_worker_estimation.format(
            repository=self.repository,
            version=self.version_app,
            bucket_name=self.bucket_name)
        worker_prediction_formated = transformation_worker_prediction.format(
            repository=self.repository,
            version=self.version_app,
            bucket_name=self.bucket_name)

        if volume_postgres_text_f is not None:
            list_return = [
                {'type': 'volume',
                 'name': 'pumpwood_transformation__volume',
                 'content': volume_postgres_text_formated, 'sleep': 10}]
        else:
            list_return = []

        list_return.extend([
            {'type': 'secrets', 'name': 'pumpwood_transformation__secrets',
             'content': secrets_text_formated, 'sleep': 5},
            {'type': 'deploy', 'name': 'pumpwood_transformation__postgres',
             'content': deployment_postgres_text_f, 'sleep': 0},
            {'type': 'deploy', 'name': 'pumpwood_transformation__app',
             'content': transformation_deployment_formated, 'sleep': 0},
            {'type': 'deploy',
             'name': 'pumpwood_transformation__estimation_worker',
             'content': worker_estimation_formated, 'sleep': 0},
            {'type': 'deploy',
             'name': 'pumpwood_transformation__prediction_worker',
             'content': worker_prediction_formated, 'sleep': 0}
        ])

        if self.firewall_ips and self.postgres_public_ip:
            services__load_balancer_template = Template(
                services__load_balancer)
            svcs__load_balancer_text = services__load_balancer_template.render(
                postgres_public_ip=self.postgres_public_ip,
                firewall_ips=self.firewall_ips
            )
            list_return.append({
                'type': 'services',
                'name': 'pumpwood_transformation__services_loadbalancer',
                'content': svcs__load_balancer_text, 'sleep': 0,
            })

        return list_return

    def end_points(self):
        """end_points."""
        return self.end_points
