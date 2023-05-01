import click
import functools
from ncclient.devices import supported_devices_cfg


def common_format_options(f):
    @click.option(
        "--format-json",
        help="If any of the available --export arguments are not used, it will print out the NETCONF payload using xmltodict (JSON)",
        is_flag=True,
    )
    @click.option(
        "--export-xml",
        help="The configuration gathered via NETCONF will be created with a filename path of this argument and exported using XML",
    )
    @click.option(
        "--export-json",
        help="The configuration gathered via NETCONF will be created with a filename path of this argument and exported using xmltodict (JSON)",
    )
    @functools.wraps(f)
    def wrapper_common_options(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper_common_options


def common_netconf_options(f):
    @click.option(
        "--host",
        help="IP Address of NETCONF Server to connect to",
        type=str,
        default="127.0.0.1",
        required=True,
    )
    @click.option(
        "--port",
        help="Port of NETCONF Server to connect to",
        type=int,
        default=830,
        required=True,
    )
    @click.option(
        "--timeout", help="SSH socket connection timeout", type=int, default=10
    )
    @click.option(
        "--username",
        help="Username to authenticate to NETCONF Server",
        envvar="NETCONF_TOOL_USERNAME",
    )
    @click.option(
        "--password",
        help="Password to authenticate to NETCONF Server",
        envvar="NETCONF_TOOL_PASSWORD",
    )
    @click.option(
        "--device-handler",
        help="Use a specific ncclient device handler to invoke vendor specific functions",
        type=click.Choice(supported_devices_cfg.keys()),
        default="default",
    )
    @click.option("--hostkey-verify", help="Verify Host Keys", is_flag=True)
    @functools.wraps(f)
    def wrapper_common_options(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper_common_options
