#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import asyncio
from pathlib import Path

import pytest
import yaml
from pytest_operator.plugin import OpsTest

METADATA = yaml.safe_load(Path("./metadata.yaml").read_text())
APP_NAME: str = METADATA["name"]
REQUIRER_NAME = "requirer-charm"


@pytest.fixture
def charm() -> str:
    """Path to the charm file to use for testing."""
    # Return str instead of pathlib.Path since python-libjuju's model.deploy(), juju deploy, and
    # juju bundle files expect local charms to begin with `./` or `/` to distinguish them from
    # Charmhub charms.
    return "./jwt-integrator_ubuntu@24.04-amd64.charm"


@pytest.fixture
def requirer_charm() -> str:
    """Path to the requirer charm file to use for testing."""
    return "./tests/integration/requirer-charm/requirer-charm_ubuntu@24.04-amd64.charm"


@pytest.mark.group(1)
@pytest.mark.abort_on_fail
async def test_build_and_deploy(charm: str, requirer_charm: str, ops_test: OpsTest) -> None:
    """Build and deploy the charm-under-test and the requirer charm."""
    await asyncio.gather(
        ops_test.model.deploy(requirer_charm, application_name=REQUIRER_NAME),
        ops_test.model.deploy(charm),
    )

    await ops_test.model.wait_for_idle(apps=[APP_NAME], status="blocked")
    assert (
        "Missing 'signing-key' or 'roles-key'"
        in ops_test.model.applications[APP_NAME].status_message
    ), "should be blocked because of invalid configuration"


@pytest.mark.group(1)
@pytest.mark.abort_on_fail
async def test_configure_jwt_integrator(ops_test: OpsTest) -> None:
    """Test setting configuration options."""
    secret_name = "signing-key-secret"
    secret_id = await ops_test.model.add_secret(name=secret_name, data_args=["signing-key=abc"])
    await ops_test.model.grant_secret(secret_name=secret_name, application=APP_NAME)

    configuration_parameters = {
        "signing-key": secret_id,
        "roles-key": "roles",
        "jwt-header": "Authentication",
        "subject-key": "sub",
        "required-audience": "aud",
        "required-issuer": "iss",
        "jwt-clock-skew-tolerance": "30",
    }

    # apply new configuration options
    await ops_test.model.applications[APP_NAME].set_config(configuration_parameters)
    await ops_test.model.wait_for_idle(apps=[APP_NAME], status="blocked")
    assert (
        "no relation for jwt interface" in ops_test.model.applications[APP_NAME].status_message
    ), "should be blocked because of missing relation"


@pytest.mark.group(1)
@pytest.mark.abort_on_fail
async def test_relate_client_charm(ops_test: OpsTest) -> None:
    """Test normal client charm relation."""
    await ops_test.model.integrate(APP_NAME, REQUIRER_NAME)
    await ops_test.model.wait_for_idle(apps=[APP_NAME, REQUIRER_NAME], status="active")
