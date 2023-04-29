import click
from redis import Redis
from loguru import logger
from ncclient import manager
from ncclient.transport.errors import SSHError, AuthenticationError
from netconf_tool.subscription import netconf_tool_cli_subscription
from netconf_tool.decorators import common_netconf_options


@netconf_tool_cli_subscription.command("redis-pubsub")
@common_netconf_options
@click.option(
    "--redis-host", help="Redis server to connect to", type=str, default="127.0.0.1"
)
@click.option("--redis-port", help="Port for Redis server", type=int, default=6379)
@click.option(
    "--redis-channel",
    help="Channel to publish message to",
    type=str,
    default="netconf_tool:all_events",
)
def cli_subscription_redis_pubsub(
    host: str,
    port: int,
    username: str,
    password: str,
    device_handler: str,
    hostkey_verify: bool,
    redis_host: str,
    redis_port: int,
    redis_channel: str,
):
    """Create a local event listener using <create-subscription> and redirect to a redis pubsub channel"""
    redis = Redis(host=redis_host, port=redis_port)
    logger.info(f"Checking if Redis server {redis_host}:{redis_port} is available")

    try:
        redis.ping()
        logger.success("Redis server is available...")
    except Exception as err:
        logger.error(err)
        exit()

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

                    data = event.notification_xml
                    redis.publish(channel=redis_channel, message=data)
                    logger.success(f"Published message to Redis Server:\n{data}")
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
