import click
from pkg_resources import iter_entry_points
from click_plugins import with_plugins


@with_plugins(iter_entry_points("netconf_tool.plugins"))
@click.group()
def cli():
    """CLI Application with plugin based architecture to interact with NETCONF Servers"""


# Import any group commands below here
from netconf_tool import operations, subscription, yangcli
