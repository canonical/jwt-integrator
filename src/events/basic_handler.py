#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Basic event handlers."""

import logging

import ops
from ops import Object

from literals import JWT_CONFIG_RELATION

logger = logging.getLogger(__name__)


class BasicEvents(Object):
    """Handle all base and etcd related events."""

    def __init__(self, charm):
        super().__init__(charm, key="basic_events")
        self.charm = charm

        # --- Basic charm events ---
        self.framework.observe(self.charm.on.start, self._on_start)
        self.framework.observe(self.charm.on.update_status, self._on_update_status)
        self.framework.observe(self.charm.on.config_changed, self._on_config_changed)
        self.framework.observe(self.charm.on.secret_changed, self._on_secret_changed)

        # --- Relation Provider events ---
        self.framework.observe(
            self.charm.on[JWT_CONFIG_RELATION].relation_created, self._on_jwt_relation_events
        )
        self.framework.observe(
            self.charm.on[JWT_CONFIG_RELATION].relation_changed, self._on_jwt_relation_events
        )

    def _on_start(self, event: ops.StartEvent) -> None:
        """Handle the charm startup event."""
        pass

    def _on_update_status(self, event: ops.UpdateStatusEvent) -> None:
        """Handle the update_status event."""
        pass

    def _on_config_changed(self, event: ops.ConfigChangedEvent) -> None:
        """Handle the config_changed event."""
        if not self.charm.unit.is_leader():
            return

        logger.debug(f"Config changed... Current configuration: {self.charm.config}")
        self.charm.jwt_config_manager.update_provider_data()

    def _on_secret_changed(self, event: ops.SecretChangedEvent) -> None:
        """Handle the secret_changed event."""
        if not self.charm.unit.is_leader():
            return

        if not (signing_key_secret := self.charm.config.get("signing-key")):
            return

        if signing_key_secret != event.secret.id:
            return

        logger.debug(f"Processing secret-change for {signing_key_secret}")
        self.charm.jwt_config_manager.update_provider_data()

    def _on_jwt_relation_events(self, event: ops.RelationChangedEvent) -> None:
        """Handle all changes to the JWT relation from provider side."""
        if not self.charm.unit.is_leader():
            return

        self.charm.jwt_config_manager.update_provider_data()
