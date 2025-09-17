# Copyright 2025 rene
# See LICENSE file for licensing details.
#
# Learn more about testing at: https://juju.is/docs/sdk/testing

from pathlib import Path

import yaml
from helpers import status_is
from ops import testing

from src.charm import JwtIntegratorCharm
from src.literals import JWT_CONFIG_RELATION, STATUS_PEERS_RELATION
from src.statuses import CharmStatuses

METADATA = yaml.safe_load(Path("./metadata.yaml").read_text())
APP_NAME = METADATA["name"]


def _get_secret_from_state(state: testing.State, secret_id: str) -> testing.Secret:
    for secret in state.secrets:
        if secret.id == secret_id:
            return secret
    raise ValueError(f"Secret with id {secret_id} not found in state")


def test_start_no_config():
    ctx = testing.Context(JwtIntegratorCharm)

    status_peer_relation = testing.PeerRelation(id=1, endpoint=STATUS_PEERS_RELATION)
    state_in = testing.State(leader=True, relations={status_peer_relation})

    state_out = ctx.run(ctx.on.start(), state_in)
    assert status_is(state_out, CharmStatuses.CONFIG_OPTIONS_INVALID.value)


def test_start_invalid_config():
    ctx = testing.Context(JwtIntegratorCharm)

    status_peer_relation = testing.PeerRelation(id=1, endpoint=STATUS_PEERS_RELATION)
    state_in = testing.State(
        leader=True,
        config={"roles-key": "abc"},
        relations={status_peer_relation},
    )

    state_out = ctx.run(ctx.on.start(), state_in)
    assert status_is(state_out, CharmStatuses.CONFIG_OPTIONS_INVALID.value)


def test_start_no_relation():
    ctx = testing.Context(JwtIntegratorCharm)

    secret_key = "signing-key"
    secret_value = "123"
    secret_content = {secret_key: secret_value}
    secret = testing.Secret(tracked_content=secret_content, remote_grants=APP_NAME)

    status_peer_relation = testing.PeerRelation(id=1, endpoint=STATUS_PEERS_RELATION)
    state_in = testing.State(
        leader=True,
        secrets=[secret],
        config={"signing-key": secret.id, "roles-key": "abc"},
        relations={status_peer_relation},
    )

    state_out = ctx.run(ctx.on.start(), state_in)
    assert status_is(state_out, CharmStatuses.NO_PROVIDER_RELATION.value)


def test_start_happy_path():
    ctx = testing.Context(JwtIntegratorCharm)

    secret_key = "signing-key"
    secret_value = "123"
    secret_content = {secret_key: secret_value}
    secret = testing.Secret(tracked_content=secret_content, remote_grants=APP_NAME)

    status_peer_relation = testing.PeerRelation(id=1, endpoint=STATUS_PEERS_RELATION)
    jwt_relation = testing.Relation(
        id=2,
        interface="jwt",
        endpoint=JWT_CONFIG_RELATION,
        remote_app_name="test",
    )

    state_in = testing.State(
        leader=True,
        secrets=[secret],
        config={"signing-key": secret.id, "roles-key": "abc"},
        relations={status_peer_relation, jwt_relation},
    )

    state_out = ctx.run(ctx.on.start(), state_in)
    assert status_is(state_out, CharmStatuses.ACTIVE_IDLE.value)


def test_update_status_happy_path():
    ctx = testing.Context(JwtIntegratorCharm)

    secret_key = "signing-key"
    secret_value = "123"
    secret_content = {secret_key: secret_value}
    secret = testing.Secret(tracked_content=secret_content, remote_grants=APP_NAME)

    status_peer_relation = testing.PeerRelation(id=1, endpoint=STATUS_PEERS_RELATION)
    jwt_relation = testing.Relation(
        id=2,
        interface="jwt",
        endpoint=JWT_CONFIG_RELATION,
        remote_app_name="test",
    )

    state_in = testing.State(
        leader=True,
        secrets=[secret],
        config={"signing-key": secret.id, "roles-key": "abc"},
        relations={status_peer_relation, jwt_relation},
    )

    state_out = ctx.run(ctx.on.update_status(), state_in)
    assert status_is(state_out, CharmStatuses.ACTIVE_IDLE.value)


def test_jwt_relation_created():
    ctx = testing.Context(JwtIntegratorCharm)

    secret_key = "signing-key"
    secret_value = "123"
    secret_content = {secret_key: secret_value}
    secret = testing.Secret(tracked_content=secret_content, remote_grants=APP_NAME)

    status_peer_relation = testing.PeerRelation(id=1, endpoint=STATUS_PEERS_RELATION)
    jwt_relation = testing.Relation(
        id=2,
        interface="jwt",
        endpoint=JWT_CONFIG_RELATION,
        remote_app_name="test",
        remote_app_data={"requested-secrets": '["signing-key"]'},
    )

    # non-leader unit
    state_in = testing.State(
        leader=False,
        secrets=[secret],
        config={"signing-key": secret.id, "roles-key": "abc"},
        relations={status_peer_relation, jwt_relation},
    )

    state_out = ctx.run(ctx.on.relation_created(jwt_relation), state_in)
    jwt_relation_state = state_out.get_relation(jwt_relation.id)

    assert status_is(state_out, CharmStatuses.ACTIVE_IDLE.value)
    assert not jwt_relation_state.local_app_data.get("roles-key")

    # leader unit
    state_in = testing.State(
        leader=True,
        secrets=[secret],
        config={"signing-key": secret.id, "roles-key": "abc"},
        relations={status_peer_relation, jwt_relation},
    )

    state_out = ctx.run(ctx.on.relation_created(jwt_relation), state_in)
    jwt_relation_state = state_out.get_relation(jwt_relation.id)

    assert status_is(state_out, CharmStatuses.ACTIVE_IDLE.value)
    assert jwt_relation_state.local_app_data["roles-key"] == "abc"
    secret_id = jwt_relation_state.local_app_data["secret-extra"]
    relation_secret = _get_secret_from_state(state_out, secret_id)
    assert relation_secret.latest_content.get("signing-key") == "123"


def test_jwt_relation_changed():
    ctx = testing.Context(JwtIntegratorCharm)

    secret_key = "signing-key"
    secret_value = "123"
    secret_content = {secret_key: secret_value}
    secret = testing.Secret(tracked_content=secret_content, remote_grants=APP_NAME)

    status_peer_relation = testing.PeerRelation(id=1, endpoint=STATUS_PEERS_RELATION)
    jwt_relation = testing.Relation(
        id=2,
        interface="jwt",
        endpoint=JWT_CONFIG_RELATION,
        local_app_data={},
        remote_app_name="test",
        remote_app_data={},
    )

    # leader unit
    state_in = testing.State(
        leader=True,
        secrets=[secret],
        config={"signing-key": secret.id, "roles-key": "abc"},
        relations={status_peer_relation, jwt_relation},
    )

    state_out = ctx.run(ctx.on.relation_changed(jwt_relation), state_in)
    jwt_relation_state = state_out.get_relation(jwt_relation.id)

    assert status_is(state_out, CharmStatuses.ACTIVE_IDLE.value)
    assert jwt_relation_state.local_app_data["roles-key"] == "abc"
    assert not jwt_relation_state.local_app_data.get("signing-key")
    secret_id = jwt_relation_state.local_app_data["secret-extra"]
    relation_secret = _get_secret_from_state(state_out, secret_id)
    assert relation_secret.latest_content.get("signing-key") == "123"


def test_config_changed():
    ctx = testing.Context(JwtIntegratorCharm)

    secret_key = "signing-key"
    secret_value = "123"
    secret_content = {secret_key: secret_value}
    secret = testing.Secret(tracked_content=secret_content, remote_grants=APP_NAME)

    status_peer_relation = testing.PeerRelation(id=1, endpoint=STATUS_PEERS_RELATION)
    jwt_relation = testing.Relation(
        id=2,
        interface="jwt",
        endpoint=JWT_CONFIG_RELATION,
        remote_app_name="test",
        remote_app_data={},
        local_app_data={},
    )

    # non-leader unit
    state_in = testing.State(
        leader=False,
        secrets=[secret],
        config={"signing-key": secret.id, "roles-key": "xyz"},
        relations={status_peer_relation, jwt_relation},
    )

    state_out = ctx.run(ctx.on.config_changed(), state_in)
    jwt_relation_state = state_out.get_relation(jwt_relation.id)

    assert status_is(state_out, CharmStatuses.ACTIVE_IDLE.value)
    assert not jwt_relation_state.local_app_data.get("roles-key")

    # leader unit
    state_in = testing.State(
        leader=True,
        secrets=[secret],
        config={"signing-key": secret.id, "roles-key": "xyz"},
        relations={status_peer_relation, jwt_relation},
    )

    state_out = ctx.run(ctx.on.config_changed(), state_in)
    jwt_relation_state = state_out.get_relation(jwt_relation.id)

    assert status_is(state_out, CharmStatuses.ACTIVE_IDLE.value)
    assert jwt_relation_state.local_app_data["roles-key"] == "xyz"
    assert not jwt_relation_state.local_app_data.get("signing-key")


def test_jwt_secret_changed():
    ctx = testing.Context(JwtIntegratorCharm)

    secret_key = "signing-key"
    secret_value = "123"
    secret_content = {secret_key: secret_value}
    secret = testing.Secret(tracked_content=secret_content, remote_grants=APP_NAME)

    status_peer_relation = testing.PeerRelation(id=1, endpoint=STATUS_PEERS_RELATION)
    jwt_relation = testing.Relation(
        id=2,
        interface="jwt",
        endpoint=JWT_CONFIG_RELATION,
        remote_app_name="test",
        remote_app_data={"requested-secrets": '["signing-key"]'},
    )

    # non-leader unit
    state_in = testing.State(
        leader=False,
        secrets=[secret],
        config={"signing-key": secret.id, "roles-key": "abc"},
        relations={status_peer_relation, jwt_relation},
    )

    state_out = ctx.run(ctx.on.secret_changed(secret=secret), state_in)
    jwt_relation_state = state_out.get_relation(jwt_relation.id)

    assert status_is(state_out, CharmStatuses.ACTIVE_IDLE.value)
    assert not jwt_relation_state.local_app_data.get("roles-key")
    assert not jwt_relation_state.local_app_data.get("signing-key")

    # leader unit
    state_in = testing.State(
        leader=True,
        secrets=[secret],
        config={"signing-key": secret.id, "roles-key": "abc"},
        relations={status_peer_relation, jwt_relation},
    )

    state_out = ctx.run(ctx.on.secret_changed(secret=secret), state_in)
    jwt_relation_state = state_out.get_relation(jwt_relation.id)

    assert status_is(state_out, CharmStatuses.ACTIVE_IDLE.value)
    assert jwt_relation_state.local_app_data["roles-key"] == "abc"
    secret_id = jwt_relation_state.local_app_data["secret-extra"]
    relation_secret = _get_secret_from_state(state_out, secret_id)
    assert relation_secret.latest_content.get("signing-key") == "123"
