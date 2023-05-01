import click
import xmltodict
import json
from xml.dom import minidom
from xml.etree import ElementTree
from xml.etree.ElementTree import ParseError
from ncclient import manager
from ncclient.transport.errors import SSHError, AuthenticationError
from loguru import logger

from netconf_tool.operations import netconf_tool_cli_operations
from netconf_tool.decorators import common_format_options, common_netconf_options


@netconf_tool_cli_operations.command("get-config")
@common_netconf_options
@common_format_options
@click.option(
    "--datastore",
    help="Specify which datastore to retrieve configuration from",
    type=click.Choice(["running", "candidate"]),
    default="running",
)
@click.option(
    "--filter", help="Include an XML filter to filter get-config operation", type=str
)
def cli_operations_get_config(
    host: str,
    port: int,
    timeout: int,
    username: str,
    password: str,
    device_handler: str,
    hostkey_verify: bool,
    datastore: str,
    filter: str,
    format_json: bool,
    export_xml: str,
    export_json: str,
):
    """Subscribes to notifications/events in real-time and prints them to the screen for debugging/troubleshooting"""
    if filter:
        logger.debug("Performing some basic XML validation")
        try:
            ElementTree.fromstring(filter)
        except ParseError as err:
            logger.error(f"Parsing error detected with --filter: {err}")
            exit()

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
            if filter:
                configuration = m.get_config(
                    source=datastore, filter=("subtree", filter)
                )
            else:
                configuration = m.get_config(source=datastore)
    except SSHError as err:
        logger.error(err)
        exit()
    except AuthenticationError as err:
        logger.error("Unable to authenticate to NETCONF server")
        exit()
    except Exception as err:
        logger.error(f"Generic Exception caught: {err}")
        exit()

    xml_data = minidom.parseString(configuration.data_xml).toprettyxml(
        indent=" ", newl=""
    )

    if export_xml:
        with open(export_xml, "w") as out_file:
            out_file.write(xml_data)
        logger.success(f"Exported get-config operation to {export_xml} in XML format")
        exit()

    if export_json:
        json_data = xmltodict.parse(xml_data)

        with open(export_json, "w") as out_file:
            json.dump(json_data, out_file, indent=4)

        logger.success(f"Exported get-config operation to {export_json} in JSON format")
        exit()

    if format_json:
        json_data = xmltodict.parse(xml_data)
        exit(json.dumps(json_data, indent=4))

    exit(xml_data)
