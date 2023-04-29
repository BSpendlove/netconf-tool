from typing import List
from urllib.parse import urlparse
from xml.etree import ElementTree


def parse_rfc3986_uri(uri: str) -> dict:
    """Parses a URI (mainly tested with netconf capabilities) and returns a dictionary

    Args:
        uri:        URI String in the format of RFC3986
    """
    parsed_uri = urlparse(uri)
    uri_object = parsed_uri._asdict()
    if parsed_uri.query:
        queries = {}
        for query in parsed_uri.query.split("&"):
            k, v = query.split("=")
            if queries.get(k):
                raise KeyError("Query Key already exists")
            queries[k] = v

        uri_object["queries"] = queries
    return uri_object


def build_xml_from_cli_commands(command: str) -> str:
    """Builds an XML tree from CLI like commands, performs no validation and is a hack function

    Args:
        command:        CLI like commands (eg. interfaces interface config name)
    """
    commands = command.split()
    root = None
    previous_element = None

    # Dynamic build XML tree based on the root and previous elements in the list of commands
    for command in commands:
        attr = None
        xmlns = None
        if "@" in command:
            command, xmlns = command.split("@")

        if "=" in command:
            command, attr = command.split("=")

        if root is None:
            root = ElementTree.Element(command)
            if attr:
                root.text = attr

            if xmlns:
                root.attrib = {"xmlns": xmlns}
            continue

        if previous_element is None:
            previous_element = ElementTree.SubElement(root, command)
        else:
            previous_element = ElementTree.SubElement(previous_element, command)

        if attr:
            previous_element.text = attr

        if xmlns:
            previous_element.attrib = {"xmlns": xmlns}

    command_string = ElementTree.tostring(root, encoding="unicode")
    return command_string
