from netconf_tool.cli import cli


@cli.group("operations")
def netconf_tool_cli_operations() -> None:
    """Perform standard NETCONF Operations (get, get-config, edit-config, etc...)"""


from netconf_tool.operations import capabilities, get_config, get_yang
