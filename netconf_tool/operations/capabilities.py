import click
import json
from ncclient import manager
from ncclient.transport.errors import SSHError, AuthenticationError
from loguru import logger

from netconf_tool.operations import netconf_tool_cli_operations
from netconf_tool.decorators import common_netconf_options
from netconf_tool.helpers import parse_rfc3986_uri


@netconf_tool_cli_operations.command("list-server-capabilities")
@common_netconf_options
@click.option(
    "--export-json",
    help="Export server capabilities into RFC3986 compliant URIs into a JSON file",
    type=str,
)
def netconf_tool_cli_operations_list_server_capabilities(
    host: str,
    port: int,
    timout: int,
    username: str,
    password: str,
    device_handler: str,
    hostkey_verify: bool,
    export_json: str,
):
    """Print or Export all NETCONF Server capabilities"""
    logger.info(f"Attempting to establish NETCONF session to {host}:{port}")
    try:
        with manager.connect(
            host=host,
            port=port,
            timeout=timeout,
            username=username,
            password=password,
            device_params={"name": device_handler},
            hostkey_verify=hostkey_verify,
        ) as m:
            logger.success(
                f"Established NETCONF connection to {host}:{port} (Session ID: {m.session_id})"
            )
            server_capabilities = m.server_capabilities
            if not export_json:
                for capability in server_capabilities:
                    print(capability)
                exit()

            capabilities = []
            for capability in server_capabilities:
                capability = parse_rfc3986_uri(uri=capability)
                capabilities.append(capability)

            logger.info(
                f"Exporting {len(capabilities)} capabilities to JSON file: {export_json}"
            )
            with open(export_json, "w") as out_file:
                json.dump(capabilities, out_file, indent=4)
    except SSHError as err:
        logger.error(err)
    except AuthenticationError as err:
        logger.error("Unable to authenticate to NETCONF server")
    except Exception as err:
        logger.error(f"Generic Exception caught: {err}")
