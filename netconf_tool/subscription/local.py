from loguru import logger
from ncclient import manager
from ncclient.transport.errors import SSHError, AuthenticationError
from netconf_tool.subscription import netconf_tool_cli_subscription
from netconf_tool.decorators import common_netconf_options


@netconf_tool_cli_subscription.command("local")
@common_netconf_options
def cli_subscription_local(
    host: str,
    port: int,
    username: str,
    password: str,
    device_handler: str,
    hostkey_verify: bool,
):
    """Create a local event listener using <create-subscription> which will simply print out the events to the CLI"""
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
        exit()
    except AuthenticationError as err:
        logger.error("Unable to authenticate to NETCONF server")
        exit()
    except Exception as err:
        logger.error(f"Generic Exception caught: {err}")
        exit()
