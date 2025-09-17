#!/usr/bin/env python3

# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Charm State definition and parsing logic."""

import logging
from typing import TYPE_CHECKING, Optional

from data_platform_helpers.advanced_statuses.protocol import StatusesState, StatusesStateProtocol
from ops import ModelError, Object, SecretNotFoundError

from core.models import JWTAuthConfiguration, JwtProviderData
from literals import JWT_CONFIG_RELATION, STATUS_PEERS_RELATION

if TYPE_CHECKING:
    from src.charm import JwtIntegratorCharm

logger = logging.getLogger(__name__)


class State(Object, StatusesStateProtocol):
    """Properties and relations of the charm."""

    def __init__(self, charm: "JwtIntegratorCharm"):
        super().__init__(parent=charm, key="charm_state")

        self.charm = charm
        self.statuses_relation_name = STATUS_PEERS_RELATION
        self.statuses = StatusesState(self, self.statuses_relation_name)
        self.charm_config = charm.config

    @property
    def provider_data_interface(self) -> JwtProviderData:
        """Get the etcd provides interface."""
        return JwtProviderData(self.model, relation_name=JWT_CONFIG_RELATION)

    @property
    def jwt_auth_config(self) -> Optional[JWTAuthConfiguration]:
        """Return configuration parameters for JWT authentication."""
        mandatory_config_parameters = ["signing-key", "roles-key"]

        for parameter in mandatory_config_parameters:
            if self.charm_config.get(parameter) is None:
                logger.error(f"Mandatory parameter {parameter} is missing")
                return None

        signing_key_secret = self.charm_config.get("signing-key")
        try:
            if not (signing_key := self.get_secret_from_id(signing_key_secret).get("signing-key")):
                logger.error("Missing mandatory secret field for `signing-key`")
                return None
        except (ModelError, SecretNotFoundError) as e:
            logger.error(e)
            return None

        return JWTAuthConfiguration(
            signing_key=signing_key,
            roles_key=self.charm_config.get("roles-key"),
            jwt_header=self.charm_config.get("jwt-header"),
            jwt_url_parameter=self.charm_config.get("jwt-url-parameter"),
            subject_key=self.charm_config.get("subject-key"),
            required_audience=self.charm_config.get("required-audience"),
            required_issuer=self.charm_config.get("required-issuer"),
            jwt_clock_skew_tolerance=self.charm_config.get("jwt-clock-skew-tolerance"),
        )

    def get_secret_from_id(self, secret_id: str) -> dict[str, str]:
        """Resolve the given id of a Juju secret and return the content as a dict.

        Args:
            secret_id (str): The id of the secret.

        Returns:
            dict: The content of the secret.
        """
        try:
            secret_content = self.model.get_secret(id=secret_id).get_content(refresh=True)
        except SecretNotFoundError:
            raise SecretNotFoundError(f"The secret '{secret_id}' does not exist.")
        except ModelError:
            raise

        return secret_content
