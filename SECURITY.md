# Security Policy

## Supported Versions

Only the latest commit on `main` receives security fixes. There are no versioned releases at this time.

| Branch | Supported |
| ------ | --------- |
| `main` | ✅        |

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Use GitHub's built-in [private vulnerability reporting](https://github.com/nclsprsn/agent-control-spine/security/advisories/new) to submit a confidential report. This keeps the details private until a fix is available.

### What to include

- Description of the vulnerability and its potential impact
- Affected component (service name, file path, dependency)
- Steps to reproduce or a proof-of-concept
- Any suggested mitigations you have identified

### Response timeline

| Stage | Target |
| ----- | ------ |
| Acknowledgement | 48 hours |
| Initial triage | 5 business days |
| Fix or workaround for Critical/High | 30 days |
| Fix or workaround for Medium/Low | 90 days |
| Public disclosure | After fix is shipped to `main` |

We follow [coordinated vulnerability disclosure](https://en.wikipedia.org/wiki/Coordinated_vulnerability_disclosure). We will credit reporters in the advisory unless anonymity is requested.

## Security Controls

| Control | Tool | Scope |
| ------- | ---- | ----- |
| Secret scanning | Gitleaks | Every push and PR |
| Static analysis | CodeQL (Python, JS/TS, Actions) | Every push and PR |
| Dependency CVEs | pip-audit, npm-audit, Trivy (fs) | Every push and PR |
| Container CVEs | Trivy (image, CRITICAL/HIGH) | Every build |
| Dependency updates | Dependabot | Weekly, all ecosystems |
| JWT authentication | Keycloak RS256 + JWKS | All service endpoints |
| Supply-chain integrity | Actions pinned to commit SHA | CI/CD |

## Threat Model Scope

In scope for responsible disclosure:

- Authentication and authorisation bypass in any service
- SQL injection, SSRF, path traversal, or XSS in any service
- Secrets committed to the repository
- Container breakout via vulnerable OS packages
- Supply-chain attacks via dependency confusion or typosquatting

Out of scope:

- Vulnerabilities requiring physical infrastructure access
- Social engineering or phishing
- Issues in third-party managed services (Keycloak, Grafana, NATS) — report those upstream
- Findings in dev-only dependencies that are never shipped in containers
