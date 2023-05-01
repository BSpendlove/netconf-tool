import click
import re
from ncclient import manager
from ncclient.transport.errors import SSHError, AuthenticationError
from loguru import logger
from pathlib import Path

from netconf_tool.operations import netconf_tool_cli_operations
from netconf_tool.decorators import common_netconf_options
from netconf_tool.helpers import parse_rfc3986_uri


@netconf_tool_cli_operations.command("get-yang-models")
@common_netconf_options
@click.option(
    "--output-dir",
    help="Directory to output YANG Model to",
    type=str,
    default="./yang_models",
)
@click.option(
    "--regex", help="Only match modules with this regex pattern", type=str, default=""
)
def cli_operations_get_yang_models(
    host: str,
    port: int,
    timeout: int,
    username: str,
    password: str,
    device_handler: str,
    hostkey_verify: bool,
    output_dir: str,
    regex: str,
):
    """Gathers all YANG Models present on the device and writes it to the output directory"""
    output_directory = Path(output_dir)
    if not output_directory.is_dir():
        logger.info("Creating output directory and any child folders")
        output_directory.mkdir(parents=True)

    regex_pattern = re.compile(regex)
    if regex:
        logger.info(
            f"Regex pattern detected, will use '{regex_pattern.pattern}' to match YANG modules"
        )
    yang_modules = []
    n = 0
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
            for capability in server_capabilities:
                capability = parse_rfc3986_uri(uri=capability)
                if not capability.get("queries") or not capability["queries"].get(
                    "module"
                ):
                    continue
                module_name = capability["queries"]["module"]
                if regex:
                    if not re.match(regex_pattern, module_name):
                        continue

                schema = m.get_schema(module_name)
                file_path = output_directory.joinpath(f"{module_name}.yang")
                with file_path.open("w") as out_file:
                    out_file.write(schema.data)
                    n += 1

                logger.success(f"Exported module {module_name} ({file_path})")

    except SSHError as err:
        logger.error(err)
        exit()
    except AuthenticationError as err:
        logger.error("Unable to authenticate to NETCONF server")
        exit()
    except Exception as err:
        logger.error(f"Generic Exception caught: {err}")
        exit()

    logger.success(f"Exported a total of {n} YANG models")


@netconf_tool_cli_operations.command("get-yang-model")
@common_netconf_options
@click.option(
    "--name",
    help="Name of the YANG Module you want to attempt to export",
    type=str,
    required=True,
)
@click.option(
    "--output-dir",
    help="Directory to output YANG Model to",
    type=str,
    default="./yang_models",
)
def cli_operations_get_yang_model(
    host: str,
    port: int,
    timeout: int,
    username: str,
    password: str,
    device_handler: str,
    hostkey_verify: bool,
    name: str,
    output_dir: str,
):
    """Gathers a specific YANG Model and writes it to the output directory"""
    output_directory = Path(output_dir)
    if not output_directory.is_dir():
        logger.info("Creating output directory and any child folders")
        output_directory.mkdir(parents=True)

    yang_modules = []
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
            for capability in server_capabilities:
                capability = parse_rfc3986_uri(uri=capability)
                if not capability.get("queries") or not capability["queries"].get(
                    "module"
                ):
                    continue
                module_name = capability["queries"]["module"]
                yang_modules.append(module_name)

            if name not in yang_modules:
                logger.error(
                    "Could not find {name} in the listed devices yang models, use 'get-yang-models' to find all valid YANG models"
                )
                exit()

            schema = m.get_schema(name)
            file_path = output_directory.joinpath(f"{name}.yang")
            with file_path.open("w") as out_file:
                out_file.write(schema.data)

            logger.success(f"Exported module {name} ({file_path})")

    except SSHError as err:
        logger.error(err)
        exit()
    except AuthenticationError as err:
        logger.error("Unable to authenticate to NETCONF server")
        exit()
    except Exception as err:
        logger.error(f"Generic Exception caught: {err}")
        exit()
