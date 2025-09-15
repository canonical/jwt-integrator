# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Statuses for the JWT Integrator.

This module defines various status enums that represent the state of the charm,
"""

from enum import Enum

from data_platform_helpers.advanced_statuses.models import StatusObject


class CharmStatuses(Enum):
    """Collection of possible statuses for the charm."""

    ACTIVE_IDLE = StatusObject(status="active", message="")
    CONFIG_OPTIONS_INVALID = StatusObject(
        status="blocked", message="invalid configuration parameters, check log for more info"
    )
    NO_PROVIDER_RELATION = StatusObject(status="blocked", message="no relation for jwt interface")
