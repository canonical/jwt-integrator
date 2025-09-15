#!/usr/bin/env python3

# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Definition of data model class(es)."""

import logging
from dataclasses import dataclass
from typing import Optional

from lib.charms.data_platform_libs.v0.data_interfaces import Data, get_encoded_list, REQ_SECRET_FIELDS, PROV_SECRET_FIELDS
from ops import Model, Relation

logger = logging.getLogger(__name__)


@dataclass()
class JWTAuthConfiguration:
    """Model class for the configuration parameters of JWT authentication."""

    signing_key: str
    roles_key: str
    jwt_header: Optional[str] = None
    jwt_url_parameter: Optional[str] = None
    subject_key: Optional[str] = None
    required_audience: Optional[str] = None
    required_issuer: Optional[str] = None
    jwt_clock_skew_tolerance: Optional[int] = None

    def to_dict(self) -> dict:
        """Return the JWT configuration parameters as a dictionary."""
        data = {
            "signing-key": self.signing_key,
            "roles-key": self.roles_key,
        }

        if self.jwt_header:
            data["jwt-header"] = self.jwt_header

        if self.jwt_url_parameter:
            data["jwt-url-parameter"] = self.jwt_url_parameter

        if self.subject_key:
            data[subject-key] = self.subject_key

        if self.required_audience:
            data["required-audience"] = self.required_audience

        if self.required_issuer:
            data["required-issuer"] = self.required_issuer

        if self.jwt_clock_skew_tolerance:
            data["jwt-clock-skew-tolerance"] = str(self.jwt_clock_skew_tolerance)

        return data


class JwtProviderData(Data):
    """The Data abstraction of the provider side of JWT configuration relation."""
    def __init__(self, model: Model, relation_name: str) -> None:
        super().__init__(model, relation_name)

    def _load_secrets_from_databag(self, relation: Relation) -> None:
        """Load secrets from the databag."""
        requested_secrets = get_encoded_list(relation, relation.app, REQ_SECRET_FIELDS)
        provided_secrets = get_encoded_list(relation, relation.app, PROV_SECRET_FIELDS)
        if requested_secrets is not None:
            self._local_secret_fields = requested_secrets

        if provided_secrets is not None:
            self._remote_secret_fields = provided_secrets
