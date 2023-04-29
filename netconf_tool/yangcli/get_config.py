import click
import json
import xmltodict
from ncclient import manager
from ncclient.transport.errors import SSHError, AuthenticationError
from loguru import logger
from xml.dom import minidom
from netconf_tool.yangcli import netconf_tool_cli_yangcli
from netconf_tool.decorators import common_format_options, common_netconf_options
from netconf_tool.helpers import build_xml_from_cli_commands


@netconf_tool_cli_yangcli.command("get-config")
@common_netconf_options
@common_format_options
@click.argument("command")
@click.option(
    "--datastore",
    help="Specify which datastore to retrieve configuration from",
    type=click.Choice(["running", "candidate"]),
    default="running",
)
def netconf_tool_cli_yangcli_get_config(
    host: str,
    port: int,
    username: str,
    password: str,
    device_handler: str,
    hostkey_verify: bool,
    command: str,
    datastore: str,
    format_json: bool,
    export_xml: str,
    export_json: str,
):
    """Print or Export all NETCONF Server capabilities - note this command does not perform any validation and is just a test"""
    filter = build_xml_from_cli_commands(command)
    if not filter:
        logger.error("Unable to build XML filter")
        exit()

    logger.debug(f"Filter that will be used for get-config: {filter}")
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
            configuration = m.get_config(source=datastore, filter=("subtree", filter))
            xml_data = minidom.parseString(configuration.data_xml).toprettyxml(
                indent=" ", newl=""
            )

            if export_xml:
                with open(export_xml, "w") as out_file:
                    out_file.write(xml_data)
                logger.success(
                    f"Exported get-config operation to {export_xml} in XML format"
                )
                exit()

            if export_json:
                json_data = xmltodict.parse(xml_data)

                with open(export_json, "w") as out_file:
                    json.dump(json_data, out_file, indent=4)

                logger.success(
                    f"Exported get-config operation to {export_json} in JSON format"
                )
                exit()

            if format_json:
                json_data = xmltodict.parse(xml_data)
                exit(json.dumps(json_data, indent=4))

            exit(xml_data)

    except SSHError as err:
        logger.error(err)
    except AuthenticationError as err:
        logger.error("Unable to authenticate to NETCONF server")
    except Exception as err:
        logger.error(f"Generic Exception caught: {err}")
