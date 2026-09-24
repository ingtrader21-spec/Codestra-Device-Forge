from enum import StrEnum
from pydantic import BaseModel, Field

class Restriction(StrEnum):
    NONE="NO_RESTRICTION"; CARRIER="CARRIER_LOCK"; FINANCING="FINANCING_POLICY"
    MDM="MDM_ENROLLMENT"; FRP="ANDROID_FRP"; ACTIVATION="APPLE_ACTIVATION_LOCK"
    BOOTLOADER="OEM_BOOTLOADER_LOCK"; UNKNOWN="UNKNOWN_RESTRICTION"

class Device(BaseModel):
    id: str
    platform: str
    manufacturer: str|None=None
    model: str|None=None
    serial_masked: str|None=None
    connection_mode: str="unknown"
    esim_supported: bool|None=None
    restrictions: list[Restriction]=Field(default_factory=list)

class Integration(BaseModel):
    id: str; kind: str; installed: bool=False; available: bool=False; detail: str=""

class LabTarget(BaseModel):
    id: str; kind: str; synthetic: bool=True; state: str="restricted"
