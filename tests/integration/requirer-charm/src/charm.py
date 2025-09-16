#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import logging

import ops
from charms.data_platform_libs.v0.data_interfaces import RequirerData

logger = logging.getLogger(__name__)

JWT_CONFIG_RELATION = "jwt-configuration"


class JwtConfigurationRequires(RequirerData):
    def __init__(self, model, relation_name: str):
        super().__init__(
            model,
            relation_name,
            additional_secret_fields=["signing-key"],
        )


class RequirerCharmCharm(ops.CharmBase):
    """Charm the service."""

    def __init__(self, framework: ops.Framework):
        super().__init__(framework)

        self.jwt_requires = JwtConfigurationRequires(self.model, relation_name=JWT_CONFIG_RELATION)

        # --- EVENT HANDLERS ---
        framework.observe(self.on.start, self._on_start)
        framework.observe(self.on.secret_changed, self._on_secret_changed)
        self.framework.observe(
            self.on[JWT_CONFIG_RELATION].relation_created, self._on_jwt_relation_created
        )
        self.framework.observe(
            self.on[JWT_CONFIG_RELATION].relation_changed, self._on_jwt_relation_changed
        )

    @property
    def jwt_relation(self) -> ops.Relation | None:
        """Return the jwt relation if present."""
        return self.jwt_requires.relations[0] if len(self.jwt_requires.relations) else None

    def _on_start(self, event: ops.StartEvent) -> None:
        """Handle the charm startup event."""
        self.unit.status = ops.ActiveStatus()

    def _on_secret_changed(self, event: ops.SecretChangedEvent) -> None:
        """Handle changed secret data."""
        if not (relation := self.jwt_requires._relation_from_secret_label(event.secret.label)):
            logger.debug("Updated secret not relevant")
            return

        if event.secret.label != self.jwt_requires._generate_secret_label(
                relation.name,
                relation.id,
                "extra",
        ):
            logging.debug("Updated secret not relevant")
            return

        relation_data = self.jwt_requires.fetch_relation_data([self.jwt_relation.id])
        logger.info(f"relation data: {relation_data}")

    def _on_jwt_relation_created(self, event: ops.RelationCreatedEvent) -> None:
        """Handle relation setup."""
        pass

    def _on_jwt_relation_changed(self, event: ops.RelationChangedEvent) -> None:
        """Handle changed relation data."""
        if not self.jwt_relation:
            return

        relation_data = self.jwt_requires.fetch_relation_data([self.jwt_relation.id])
        logger.info(f"relation data: {relation_data}")


if __name__ == "__main__":  # pragma: nocover
    ops.main(RequirerCharmCharm)
