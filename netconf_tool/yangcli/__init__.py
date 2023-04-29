from netconf_tool.cli import cli


@cli.group("yangcli")
def netconf_tool_cli_yangcli() -> None:
    """Attempts to build a dynamic XML payload based on a tradtional CLI input"""


from netconf_tool.yangcli import get_config
