#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Charmed operator for providing JWT authentication configuration to a charmed application."""

import logging

import ops
from data_platform_helpers.advanced_statuses.handler import StatusHandler

from core.context import Context
from events.basic_handler import BasicEvents
from managers.jwt_config import JwtConfigManager

logger = logging.getLogger(__name__)


class JwtIntegratorCharm(ops.CharmBase):
    """Charm the service."""

    def __init__(self, framework: ops.Framework):
        super().__init__(framework)
        self.context = Context(config=self.config)

        # --- MANAGERS ---
        self.jwt_config_manager = JwtConfigManager(context=self.context)

        # --- STATUS HANDLER ---
        self.status = StatusHandler(  # priority order
            self,
            self.jwt_config_manager,
        )

        # --- EVENT HANDLERS ---
        self.basic_events = BasicEvents(self)


if __name__ == "__main__":  # pragma: nocover
    ops.main(JwtIntegratorCharm)
