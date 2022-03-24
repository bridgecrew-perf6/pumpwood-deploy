"""Google Trends data crawler module."""
import os
import base64
from pumpwood_deploy.microservices.postgres.postgres import \
    create_ssl_key_ssl_crt
from jinja2 import Template


class GoogleTrendsCrawler:
    """
    Class to help deployment of BigData Corp Crawler.

    This class helps to get information from bigdata corp APIs.
    https://www.bigdatacorp.info/
    """

    def __init__(self, db_username, db_password, micro_username,
                 micro_password, bucket_name, disk_size, disk_name,
                 postgres_public_ip, firewall_ips,
                 version_queue_manager, version_puller, version_pusher,
                 repository: str="gcr.io/repositorio-geral-170012",
                 workers_timeout: int=300):):
        """
        __init__.

        Args:
            db_username (str): database username.
            db_password (str): database password.
            micro_username (str): microservice username.
            micro_password (str): microservice password.
            disk_size (str): Disk size for postgres.
            disk_name (str): Disk name for postgres.
            postgres_public_ip (str): Public postres IP to use on load
                                      balancer.
            version_queue_manager (str): Version of the queue manager.
            version_puller (str): Version of the puller.
            version_pusher (str): Version of the pusher.
        Kwargs:
            repository (str): Path to repository.
            workers_timeout (int): Time in seconds to wait for guinicorn worker
                response.
        """
        postgres_certificates = create_ssl_key_ssl_crt()

        self._db_username = base64.b64encode(db_username.encode()).decode()
        self._db_password = base64.b64encode(db_password.encode()).decode()
        self._micro_username = base64.b64encode(
            micro_username.encode()).decode()
        self._micro_password = base64.b64encode(
            micro_password.encode()).decode()

        self._ssl_crt = base64.b64encode(
            postgres_certificates['ssl_crt'].encode()).decode()
        self._ssl_key = base64.b64encode(
            postgres_certificates['ssl_key'].encode()).decode()

        self.postgres_public_ip = postgres_public_ip
        self.bucket_name = bucket_name
        self.disk_size = disk_size
        self.disk_name = disk_name
        self.base_path = os.path.dirname(__file__)

        self.repository = repository

        self.workers_timeout = workers_timeout
        self.firewall_ips = firewall_ips

        self.version_queue_manager = version_queue_manager
        self.version_puller = version_puller
        self.version_pusher = version_pusher

    def create_deployment_file(self):
        """Create Google Trends deployment files."""
        with open(os.path.join(self.base_path, 'resources_yml/secrets.yml'),
                  'r') as file:
            secrets_text = file.read()deployment_scheduler_formated
        secrets_text_formated = secrets_text.format(
            db_username=self._db_username,
            db_password=self._db_password,
            micro_username=self._micro_username,
            micro_password=self._micro_password,
            ssl_key=self._ssl_key,
            ssl_crt=self._ssl_crt,)

        with open(os.path.join(self.base_path, 'resources_yml/volume_postgres.yml'),
                  'r') as file:
            volume_postgres_text = file.read()
        volume_postgres_text_formated = volume_postgres_text.format(
            disk_size=self.disk_size,
            disk_name=self.disk_name)

        with open(os.path.join(self.base_path,
                               'resources_yml/deployment_postgres.yml'),
                  'r') as file:
            deployment_postgres_text = file.read()

        with open(os.path.join(self.base_path,
                               'resources_yml/deployment_queue_manager.yml'),
                  'r') as file:
            deployment_queue_manager_text = file.read()
        deployment_queue_manager_text_formated = \
            deployment_queue_manager_text.format(
                repository=self.repository,
                bucket_name=self.bucket_name,
                version=self.version_queue_manager,
                workers_timeout=self.workers_timeout)

        with open(os.path.join(self.base_path, 'resources_yml/deployment_puller.yml'),
                  'r') as file:
            deployment_puller_text = file.read()
        deployment_puller_text_formated = deployment_puller_text.format(
                repository=self.repository, bucket_name=self.bucket_name,
                version=self.version_puller)

        with open(os.path.join(self.base_path,
                  'resources_yml/deployment_pusher.yml'), 'r') as file:
            deployment_pusher_text = file.read()
        deployment_pusher_text_formated = deployment_pusher_text.format(
            repository=self.repository, bucket_name=self.bucket_name,
            version=self.version_pusher)

        with open(os.path.join(self.base_path, 'resources_yml/services.yml'),
                  'r') as file:
            services_text_formated = file.read()

        list_return = [{
                'type': 'services',
                'name': 'crawler__google_trends__services',
                'content': services_text_formated, 'sleep': 0},
            {
                'type': 'secrets',
                'name': 'crawler__google_trends__secrets',
                'content': secrets_text_formated, 'sleep': 5},
            {
                'type': 'volume', 'name': 'crawler__google_trends__volume',
                'content': volume_postgres_text_formated, 'sleep': 10},
            {
                'type': 'deploy',
                'name': 'crawler__google_trends__postgres',
                'content': deployment_postgres_text, 'sleep': 0},
            {
                'type': 'deploy',
                'name': 'crawler__google_trends__queue_manager',
                'content': deployment_queue_manager_text_formated, 'sleep': 0},
            {
                'type': 'deploy',
                'name': 'crawler__google_trends__puller',
                'content': deployment_puller_text_formated, 'sleep': 0},
            {
                'type': 'deploy',
                'name': 'crawler__google_trends__pusher',
                'content': deployment_scheduler_formated, 'sleep': 0}, ]

        if self.firewall_ips and self.postgres_public_ip:
            with open(os.path.join(self.base_path,
                                   'resources_yml/services__load_balancer.jinja2'),
                      'r') as file:
                services__load_balancer_template = Template(file.read())
            svcs__load_balancer_text = services__load_balancer_template.render(
                postgres_public_ip=self.postgres_public_ip,
                firewall_ips=self.firewall_ips)

            list_return.append({
                'type': 'services',
                'name': 'crawler__google_trends__services_loadbalancer',
                'content': svcs__load_balancer_text, 'sleep': 0})
        return list_return

    def end_points(self):
        """Return microservices end-points."""
        return self.end_points
