# custom_components\shabman\const.py

"""Constants for the shABman integration."""

DOMAIN = "shabman"
CONF_DEVICE_IP = "device_ip"
CONF_DEVICE_TYPE = "device_type"

# Update interval in seconds
UPDATE_INTERVAL = 30

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
