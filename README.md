# JWT-integrator
[![Charmhub](https://charmhub.io/jwt-integrator/badge.svg)](https://charmhub.io/jwt-integrator)
[![Release](https://github.com/canonical/jwt-integrator/actions/workflows/release.yaml/badge.svg)](https://github.com/canonical/jwt-integrator/actions/workflows/release.yaml)
[![Tests](https://github.com/canonical/jwt-integrator/actions/workflows/ci.yaml/badge.svg)](https://github.com/canonical/jwt-integrator/actions/workflows/ci.yaml)

## Description

A provider charm for JWT authentication configuration.

## Usage

### Deploying the JWT Integrator

Currently, the integrator supports bare-metal/virtual-machine deployments.

#### Charmhub

```shell
juju deploy jwt-integrator --channel 1/edge
```

### Configuring the Integrator

To configure the jwt-integrator charm, you may provide the following configuration options:
  
- `signing-key`: the signing key(s) used to verify the token, provided as a user secret.
- `roles-key`: the key in the JSON payload that stores the user’s roles.
- `jwt-header`: the HTTP header in which the token is transmitted (typically the `Authorization` header).
- `jwt-url-parameter`: the HTTP URL parameter to use if not using the `jwt-header`.
- `subject-key`: the key in the JSON payload that stores the username.
- `required-audience`: the name of the audience that the JWT must specify.
- `required-issuer`:the target issuer of JWT stored in the JSON payload.
- `jwt-clock-skew-tolerance`: time in seconds that is tolerated as clock disparity between the authentication parties.

The only mandatory fields for the integrator are `signing-key` and `roles-key`.

To create a user secret containing the `signing-key`, follow these steps:

```shell
juju add-secret jwt-key signing-key="eyJhbGciOiAiSFMyNTYiLCAidHlwIjogI..."
secret:<your-secret-id>

juju grant-secret jwt-key jwt-integrator

juju config jwt-integrator signing-key=secret:<your-secret-id>
```

Provide the key used for signing your self-contained JWT's instead of the example above.

## Relations 

Relations are supported via the `jwt` interface. To create a relation:

```bash
juju integrate jwt-integrator application
```

To remove the relation:
```bash
juju remove-relation jwt-integrator application
```

## Security

Security issues in the Charmed jwt Integrator Operator can be reported through [LaunchPad](https://wiki.ubuntu.com/DebuggingSecurity#How%20to%20File). Please do not file GitHub issues about security issues.

## Contributing

Please see the [Juju SDK docs](https://juju.is/docs/sdk) for guidelines on enhancements to this charm following best practice guidelines, and [CONTRIBUTING.md](https://github.com/canonical/jwt-integrator/blob/main/CONTRIBUTING.md) for developer guidance.

