from netconf_tool.cli import cli


@cli.group("subscription")
def netconf_tool_cli_subscription() -> None:
    """Tools to deal with <create-subscription> and NETCONF based events/notifications"""


from netconf_tool.subscription import local, rabbitmq, redis
