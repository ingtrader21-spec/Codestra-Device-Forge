# Codestra Device Forge

Codestra Device Forge is the control plane for authorized mobile-device discovery, OS/firmware workflows, SIM/eSIM provisioning, device management, security analysis, and an isolated research lab.

## Scope

- Android transport: ADB / Fastboot
- Apple transport: libimobiledevice
- Samsung firmware adapter: Heimdall
- eSIM adapter: OpenEUICC / EasyEUICC where supported
- Android management adapter: MDMesh
- Security analysis: MobSF
- Lab virtualization: Android Emulator / QEMU
- Protocol analysis for Codestra-owned lab services: mitmproxy / Wireshark

## Safety boundary

Real-device operations must not bypass carrier locks, financing locks, MDM ownership controls, Android FRP, Apple Activation Lock, stolen-device protections, or similar controls. Device Forge detects and reports such restrictions and routes them to authorized release workflows. Bypass research is confined to synthetic/emulated Codestra-owned lab targets.

## Initial architecture

```text
Device Forge API
├── AndroidTransport
│   ├── ADB
│   └── Fastboot
├── AppleTransport
│   └── libimobiledevice
├── FirmwareProvider
│   └── Heimdall
├── EsimProvider
│   └── OpenEUICC / EasyEUICC
├── ManagementProvider
│   └── MDMesh
├── SecurityProvider
│   └── MobSF
└── ResearchLab
    ├── Android Emulator
    ├── QEMU
    ├── Carrier emulator
    ├── Financing emulator
    ├── MDM emulator
    ├── FRP emulator
    └── Activation-lock emulator
```

See `docs/MASTER_MISSION.md` for the implementation gates.
