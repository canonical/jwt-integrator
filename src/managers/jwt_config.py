#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Manager for handling configuration building and status computation."""

import logging

from data_platform_helpers.advanced_statuses.models import StatusObject
from data_platform_helpers.advanced_statuses.protocol import ManagerStatusProtocol
from data_platform_helpers.advanced_statuses.types import Scope
from ops.model import ConfigData

from core.context import Context
from statuses import CharmStatuses

logger = logging.getLogger(__name__)


class JwtConfigManager(ManagerStatusProtocol):
    """Handle the configuration of etcd."""

    name: str = "jwt-config"
    context: Context
    config: ConfigData

    def __init__(
        self,
        context: Context,
    ):
        self.context = context

    def get_statuses(self, scope: Scope, recompute: bool = False) -> list[StatusObject]:
        """Compute the Cluster manager's statuses."""
        status_list: list[StatusObject] = []

        if not self.context.jwt_auth_config:
            status_list.append(CharmStatuses.CONFIG_OPTIONS_INVALID.value)

        if not self.context.provider_data.relations:
            status_list.append(CharmStatuses.NO_PROVIDER_RELATION.value)

        return status_list if status_list else [CharmStatuses.ACTIVE_IDLE.value]

    def update_provider_data(self):
        """Update the contents of the relation data bag."""
        if not self.context.provider_data.relations:
            logger.info("No relation to update")
            return

        if not self.context.jwt_auth_config:
            logger.error("Configuration settings invalid, cannot update provider data")
            return

        for relation in self.context.provider_data.relations:
            self.context.provider_data.update_relation_data(
                relation.id, self.context.jwt_auth_config.to_dict()
            )
            logger.info(f"Updated relation id {relation.id}")
