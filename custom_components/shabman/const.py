"""Constants for the shABman integration."""

DOMAIN = "shabman"
CONF_DEVICE_IP = "device_ip"
CONF_DEVICE_TYPE = "device_type"

# Shelly device types that support scripting (Gen2+)
SUPPORTED_DEVICES = [
    "Shelly Plus 1",
    "Shelly Plus 1PM",
    "Shelly Plus 2PM",
    "Shelly Plus i4",
    "Shelly Plus Plug S",
    "Shelly Plus Plug US",
    "Shelly Plus H&T",
    "Shelly Pro 1",
    "Shelly Pro 1PM",
    "Shelly Pro 2",
    "Shelly Pro 2PM",
    "Shelly Pro 3",
    "Shelly Pro 4PM",
    "Shelly Pro EM",
    "Shelly BLU Gateway",
]

# Update interval in seconds
UPDATE_INTERVAL = 30

# Script groups for organization
SCRIPT_GROUPS = [
    "BLE Gateway",
    "Energy Management",
    "Automation",
    "Sensors",
    "Notifications",
    "Custom",
]

# API endpoints
RPC_SHELLY_GET_DEVICE_INFO = "/rpc/Shelly.GetDeviceInfo"
RPC_SCRIPT_LIST = "/rpc/Script.List"
RPC_SCRIPT_CREATE = "/rpc/Script.Create"
RPC_SCRIPT_DELETE = "/rpc/Script.Delete"
RPC_SCRIPT_PUT_CODE = "/rpc/Script.PutCode"
RPC_SCRIPT_GET_CODE = "/rpc/Script.GetCode"
RPC_SCRIPT_START = "/rpc/Script.Start"
RPC_SCRIPT_STOP = "/rpc/Script.Stop"
RPC_SCRIPT_GET_STATUS = "/rpc/Script.GetStatus"
