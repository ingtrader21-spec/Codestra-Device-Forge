# Codestra Device Forge — Master Implementation Mission

## Objective

Build Device Forge into a self-hosted platform for authorized device discovery, compatibility analysis, verified firmware/OS workflows, backup/recovery, SIM/eSIM provisioning, device management, mobile-app security analysis, and an isolated restriction-security lab.

## Gates

1. Baseline repository and runtime inventory.
2. Device discovery and normalized device model.
3. Compatibility engine.
4. Image/provider registry and provenance.
5. Secure download, checksum, and signature verification.
6. Backup and recovery manifest.
7. Installation planning and explicit approval gate.
8. Installation state machine.
9. Physical-action checkpoints.
10. Post-install hardware certification.
11. SIM/eSIM provisioning and connectivity validation.
12. Restriction diagnostics and authorized-release workflow.
13. Device-management integrations.
14. Open-source adapters: ADB/Fastboot, libimobiledevice, Heimdall, OpenEUICC/EasyEUICC, MDMesh, MobSF.
15. Security research lab using only synthetic/emulated Codestra-owned targets.
16. Web UI, API, persistence, RBAC, audit, telemetry, and CI.
17. Real-device certification on at least one authorized lab device.

## Required API namespaces

- /api/v1/integrations
- /api/v1/devices
- /api/v1/compatibility
- /api/v1/images
- /api/v1/backups
- /api/v1/installations
- /api/v1/esim
- /api/v1/management
- /api/v1/security/scans
- /api/v1/restrictions
- /api/v1/lab/targets
- /api/v1/lab/experiments
- /api/v1/reports

## Destructive-operation rule

No firmware or OS change can execute unless the chain has reached:

IDENTIFIED -> COMPATIBILITY_VERIFIED -> IMAGE_VERIFIED -> BACKUP_COMPLETE -> PLAN_READY -> APPROVED -> PRECHECK

## SIM/eSIM rule

Authorized flow only:

DETECT_EUICC -> VALIDATE_PROFILE -> APPROVAL -> PROVISION -> ACTIVATE -> NETWORK_TEST

Do not use SIM/eSIM manipulation as a substitute for clearing carrier, financing, MDM, FRP, Activation Lock, or other ownership/security restrictions.

## Research-lab rule

Bypass experimentation is limited to synthetic/emulated lab targets with Codestra-owned identifiers, keys, services, and accounts. The lab must never target production Apple, Google, carrier, OEM, financing, or third-party MDM services.

## Definition of Done

Do not report COMPLETE because containers start or code compiles. COMPLETE requires working integration evidence, automated tests, audit events, UI evidence, and at least one authorized real-device discovery flow. Any unmet gate must be reported as PARTIAL.
