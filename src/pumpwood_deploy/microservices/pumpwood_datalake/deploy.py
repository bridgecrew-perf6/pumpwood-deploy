"""PumpWood DataLake Microservice Deploy."""

import os
import base64
from pumpwood_deploy.microservices.postgres.postgres import \
    create_ssl_key_ssl_crt
from jinja2 import Template
from .resources.yml__resources import (
    app_deployment, worker_deployment, deployment_postgres,
    secrets, services__load_balancer, volume_postgres,
    test_postgres)


class PumpWoodDatalakeMicroservice:
    """PumpWoodDatalakeMicroservice."""

    def __init__(self, db_password: str, microservice_password: str,
                 bucket_name: str, version_app: str, version_worker: str,
                 disk_name: str = None, disk_size: str = None,
                 postgres_public_ip: str = None, firewall_ips: list = None,
                 repository: str = "gcr.io/repositorio-geral-170012",
                 workers_timeout: int = 300, n_chunks: int = 5,
                 chunk_size: int = 5000, replicas: int = 1,
                 test_db_version: str = None,
                 test_db_repository: str = "gcr.io/repositorio-geral-170012",
                 debug: str = "FALSE"):
        """
        __init__: Class constructor.

        Args:
            db_password (str): Password for database.
            microservice_password(str): Microservice password.
            postgres_public_ip (str): Postgres public IP.
            firewall_ips (list): List the IPs allowed to connect to datalake.
            bucket_name (str): Name of the bucket (Storage)
            version_app (str): Verison of the App Image.
            version_worker (str): Verison of the Worker Image.

        Kwargs:
          disk_size (str): Disk size (ex.: 50Gi, 100Gi)
          disk_name (str): Name of the disk that will be used in postgres
          replicas (int) = 1: Number of replicas in app deployment.
          workers_timeout (str): Time to workout time for guicorn workers.
          n_chunks (str) = 5: n chunks working o data loader.
          chunk_size (str) = 5000: Size of the datalake chunks.
          repository (str) = "gcr.io/repositorio-geral-170012": Repository to
            pull Image
          test_db_version (str): Set a test database with version.
          test_db_repository (str): Define a repository for the test
            database.
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

        self.bucket_name = bucket_name
        self.disk_size = disk_size
        self.disk_name = disk_name
        self.base_path = os.path.dirname(__file__)

        self.n_chunks = n_chunks
        self.chunk_size = chunk_size
        self.workers_timeout = workers_timeout

        self.repository = repository
        self.debug = debug
        self.version_app = version_app
        self.version_worker = version_worker
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
            disk_size=self.disk_size, disk_name=self.disk_name)

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

        deployment_queue_manager_text_frmtd = \
            app_deployment.format(
                repository=self.repository,
                version=self.version_app,
                bucket_name=self.bucket_name,
                workers_timeout=self.workers_timeout,
                replicas=self.replicas,
                debug=self.debug)
        worker_deployment_text_frmted = worker_deployment.format(
            repository=self.repository, version=self.version_worker,
            n_chunks=self.n_chunks, chunk_size=self.chunk_size,
            bucket_name=self.bucket_name)

        if volume_postgres_text_f is not None:
            list_return = [
                {'type': 'volume', 'name': 'pumpwood_datalake__volume',
                 'content': volume_postgres_text_formated, 'sleep': 10}]
        else:
            list_return = []

        list_return.extend([
            {'type': 'secrets', 'name': 'pumpwood_datalake__secrets',
             'content': secrets_text_formated, 'sleep': 5},

            {'type': 'deploy', 'name': 'pumpwood_datalake__postgres',
             'content': deployment_postgres_text_f, 'sleep': 0},

            {'type': 'deploy', 'name': 'pumpwood_datalake__deploy',
             'content': deployment_queue_manager_text_frmtd, 'sleep': 0},

            {'type': 'deploy', 'name': 'pumpwood_datalake_dataloader__worker',
             'content': worker_deployment_text_frmted, 'sleep': 0}])

        if self.firewall_ips is not None and self.postgres_public_ip:
            services__load_balancer_template = Template(
                services__load_balancer)
            svcs__load_balancer_text = services__load_balancer_template.render(
                postgres_public_ip=self.postgres_public_ip,
                firewall_ips=self.firewall_ips)
            list_return.append({
                'type': 'services',
                'name': 'pumpwood_datalake__services_loadbalancer',
                'content': svcs__load_balancer_text, 'sleep': 0})

        return list_return
