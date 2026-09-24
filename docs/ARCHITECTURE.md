# Architecture

Device Forge is the authority layer. Third-party tools are adapters, not public endpoints.

## Production-capable lanes
- Read-only Android discovery through ADB.
- Read-only Apple discovery through libimobiledevice.
- Heimdall detection is an adapter dependency; destructive flashing remains approval-gated.
- eSIM provisioning accepts only authorized profiles and platform-supported flows.
- MDM integration is for devices the operator is authorized to manage.
- MobSF is used for authorized application analysis.

## Research lane
Carrier, financing, MDM, FRP and activation-lock bypass experiments run only against synthetic/emulated Codestra-owned targets. The API rejects non-synthetic research targets.

## Next hardware gate
Actual hardware certification requires execution on the Ubuntu Device Forge host with authorized Android/Apple/Samsung test devices attached.
