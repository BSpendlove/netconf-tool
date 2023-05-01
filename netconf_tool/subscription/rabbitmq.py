import click
import pika
from pika.exceptions import AMQPConnectionError
from loguru import logger
from ncclient import manager
from ncclient.transport.errors import SSHError, AuthenticationError
from netconf_tool.subscription import netconf_tool_cli_subscription
from netconf_tool.decorators import common_netconf_options


@netconf_tool_cli_subscription.command("rabbitmq")
@common_netconf_options
@click.option(
    "--rabbitmq-host",
    help="RabbitMQ Server to connect to",
    type=str,
    default="127.0.0.1",
)
@click.option(
    "--rabbitmq-port", help="Port for RabbitMQ server", type=int, default=5672
)
@click.option(
    "--rabbitmq-queue",
    help="RabbitMQ Queue to create",
    type=str,
    default="netconf_tool",
)
@click.option("--rabbitmq-exchange", help="RabbitMQ Exchange", type=str, default="")
@click.option(
    "--rabbitmq-routing-key",
    help="RabbitMQ Routing Key",
    type=str,
    default="all_events",
)
@click.option(
    "--rabbitmq-username",
    help="Username to authenticate if authentication is used",
    type=str,
)
@click.option(
    "--rabbitmq-password",
    help="Password to authenticate if authentication is used",
    type=str,
)
def cli_subscription_rabbitmq(
    host: str,
    port: int,
    timeout: int,
    username: str,
    password: str,
    device_handler: str,
    hostkey_verify: bool,
    rabbitmq_host: str,
    rabbitmq_port: int,
    rabbitmq_queue: str,
    rabbitmq_exchange: str,
    rabbitmq_routing_key: str,
    rabbitmq_username: str,
    rabbitmq_password: str,
):
    """Create a local event listener using <create-subscription> and redirect to a rabbitmq host"""
    parameters = pika.ConnectionParameters(rabbitmq_host, rabbitmq_port, "/")

    if rabbitmq_username and rabbitmq_password:
        parameters.credentials = pika.PlainCredentials(
            rabbitmq_username, rabbitmq_password
        )

    try:
        connection = pika.BlockingConnection()
    except AMQPConnectionError as err:
        logger.error(
            f"Unable to establish connection to RabbitMQ server {rabbitmq_host}:{rabbitmq_password}"
        )
        exit()
    channel = connection.channel()
    channel.queue_declare(queue=rabbitmq_queue)

    logger.info(
        f"Checking if RabbitMQ Server {rabbitmq_host}:{rabbitmq_port} is available"
    )

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
            m.create_subscription()
            logger.success(
                "Created Netconf Subscription, you can exit out of here using Ctrl+C"
            )

            try:
                while True:
                    logger.info("Awaiting next NETCONF <notification/>")
                    event = m.take_notification()

                    # Publish to RabbitMQ Queue
                    data = event.notification_xml
                    channel.basic_publish(
                        exchange=rabbitmq_exchange,
                        routing_key=rabbitmq_routing_key,
                        body=data,
                    )
                    logger.success(f"Published message to RabbitMQ Server:\n{data}")
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
