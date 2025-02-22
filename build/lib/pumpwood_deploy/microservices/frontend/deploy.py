"""PumpWood Frontend Module."""
import os
import base64
from pumpwood_deploy.microservices.frontend.resources.yml__resources import (
    deployment_yml, secrets_yml)


class PumpwoodFrontEndMicroservice:
    """Create Angular front-end deploy filess."""

    def __init__(self, version: str, gateway_public_ip: str,
                 microservice_password: str, debug: str = 'FALSE',
                 repository: str = "gcr.io/repositorio-geral-170012"):
        """__init__."""
        self.repository = repository
        self.version = version
        self.gateway_public_ip = gateway_public_ip
        self.debug = debug
        self._microservice_password = base64.b64encode(
            microservice_password.encode()).decode()
        self.base_path = os.path.dirname(__file__)

    def create_deployment_file(self):
        """create_deployment_file."""
        deployment_text_f = deployment_yml.format(
            repository=self.repository,
            gateway_public_ip=self.gateway_public_ip,
            debug=self.debug,
            version=self.version)

        secrets_text_f = secrets_yml.format(
            microservice_password=self._microservice_password)

        list_return = [
            {'type': 'secrets', 'name': 'pumpwood_frontend__secrets',
             'content': secrets_text_f, 'sleep': 5},
            {'type': 'deploy', 'name': 'pumpwood_frontend__deploy',
             'content': deployment_text_f, 'sleep': 10},
        ]

        return list_return
