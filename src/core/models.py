#!/usr/bin/env python3

# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Definition of data model class(es)."""

import logging
from dataclasses import dataclass
from typing import Optional

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
            "jwt-header": self.jwt_header,
            "jwt-url-parameter": self.jwt_url_parameter,
            "subject-key": self.subject_key,
            "required-audience": self.required_audience,
            "required-issuer": self.required_issuer,
            "jwt-clock-skew-tolerance": self.jwt_clock_skew_tolerance,
        }

        return data
