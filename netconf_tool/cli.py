import click
import json
from pkg_resources import iter_entry_points
from click_plugins import with_plugins
from ncclient import manager
from ncclient.transport.errors import SSHError, AuthenticationError
from loguru import logger

from netconf_tool.decorators import netconf_common_options
from netconf_tool.helpers import parse_rfc3986_uri


@with_plugins(iter_entry_points("netconf_tool.plugins"))
@click.group()
def cli():
    """CLI Application with plugin based architecture to interact with NETCONF Servers"""


@cli.command("list-server-capabilities")
@click.option(
    "--export-json",
    help="Export server capabilities into RFC3986 compliant URIs into a JSON file",
    type=str,
)
@netconf_common_options
def cli_list_server_capabilities(
    host: str,
    port: int,
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


@cli.command("create-subscription")
@netconf_common_options
def cli_create_subscription(
    host: str,
    port: int,
    username: str,
    password: str,
    device_handler: str,
    hostkey_verify: bool,
):
    """Subscribes to notifications/events in real-time and prints them to the screen for debugging/troubleshooting"""
    logger.info(f"Attempting to establish NETCONF session to {host}:{port}")
    try:
        with manager.connect(
            host=host,
            port=port,
            username=username,
            password=password,
            device_params={"name": device_handler},
            hostkey_verify=hostkey_verify,
        ) as m:
            logger.success(
                f"Established NETCONF connection to {host}:{port} (Session ID: {m.session_id})"
            )
            m.create_subscription()
            logger.success(
                "Created Netconf Subscription, you can exit out of here using Ctrl+C"
            )

            try:
                while True:
                    logger.info("Awaiting next NETCONF <notification/>")
                    event = m.take_notification()

                    logger.info(event.notification_xml)
            except KeyboardInterrupt:
                logger.info("Stopping NETCONF Notification Subscription")
    except SSHError as err:
        logger.error(err)
    except AuthenticationError as err:
        logger.error("Unable to authenticate to NETCONF server")
    except Exception as err:
        logger.error(f"Generic Exception caught: {err}")
