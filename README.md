# netconf-tool

This is a tool aimed for developer experience / making things faster when I am trying to test NETCONF related tasks without having to rewrite a random python script. I've found myself constantly writing little python scripts for NETCONF to test functionality or even grab data such as server capabilities, setup event based notifications/subscription to test something and have probably got 100 scripts that do the same thing in different folders through the various projects I've worked on.

Therefore I've created this tool to improve my developer experience working with NETCONF. At the ease of a quick command, I want to be able to get config, try out some edit-config functionality, grab capabilities of a new vendor I am working with, test NETCONF notifications etc... and now I can and want to share my progress as I work my way through adding functionality to this tool.

Here are the reasons for the required modules:

- ncclient                  - Obvious one... Handles the low networking level of SSH/NETCONF
- click and click-plugins   - Click is an awesome tool to build CLI applications, netconf-tool is a CLI application
- loguru                    - Best logging module out there, I don't like exit() and print() statements...

This CLI application is built to load plugins using the entrypoint of netconf-tools so I may look into adding more functionality once I move over all my developer focused NETCONF tasks to this CLI project.

The plan in the future is to setup a better experience for contributers with pytest and a better pipeline however I will try my best not to break everything when I release a new version...

## Environment Variables

Use NETCONF_TOOL_USERNAME and NETCONF_TOOL_PASSWORD environment variables to prevent exposing the --username and --password arguments in your operating system CLI history.

## Feature Examples

### create-subscription

This creates a notification event subscription (RFC 5277) and displays the NETCONF payload on the screen, currently doesn't support replay functionality but is useful when developing NETCONF based alerting NMS/applications.

```bash
$ netconf-tool create-subscription --host 192.0.2.1
2023-04-28 22:12:14.299 | INFO     | netconf_tool.cli:cli_create_subscription:85 - Attempting to establish NETCONF session to 192.0.2.1:830
2023-04-28 22:12:14.662 | SUCCESS  | netconf_tool.cli:cli_create_subscription:95 - Established NETCONF connection to 192.0.2.1:830 (Session ID: 43)
2023-04-28 22:12:14.770 | SUCCESS  | netconf_tool.cli:cli_create_subscription:99 - Created Netconf Subscription, you can exit out of here using Ctrl+C
2023-04-28 22:12:14.770 | INFO     | netconf_tool.cli:cli_create_subscription:105 - Awaiting next NETCONF <notification/>
2023-04-28 22:12:23.035 | INFO     | netconf_tool.cli:cli_create_subscription:108 - <?xml version="1.0" encoding="UTF-8"?>
<notification xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0">
  <eventTime>2023-04-28T22:12:22Z</eventTime>
  <netconf-config-change xmlns="urn:ietf:params:xml:ns:yang:ietf-netconf-notifications">
    <changed-by>
      <username>netconftool</username>
      <session-id>0</session-id>
    </changed-by>
    <datastore>running</datastore>
    <edit>
      <target
        xmlns:oc-if="http://openconfig.net/yang/interfaces">/oc-if:interfaces/oc-if:interface[name='xe16']/oc-if:config</target>
      <operation>merge</operation>
    </edit>
    <edit>
      <target
        xmlns:oc-netinst="http://openconfig.net/yang/network-instance">/oc-netinst:network-instances/oc-netinst:network-instance/oc-netinst:interfaces/oc-netinst:interface</target>
      <operation>merge</operation>
    </edit>
  </netconf-config-change>
</notification>
```

### list-server-capabilities

Prints the server capabilities unless --export-json flag is used, if this flag is used then each capability will be parsed into an RFC3986 compliant object/dictionary and then exported into the relevant filename used in this argument.

```bash
$ netconf-tool list-server-capabilities --host 192.0.2.1
2023-04-28 22:14:39.493 | INFO     | netconf_tool.cli:cli_list_server_capabilities:36 - Attempting to establish NETCONF session to 192.0.2.1:830
2023-04-28 22:14:39.858 | SUCCESS  | netconf_tool.cli:cli_list_server_capabilities:46 - Established NETCONF connection to 192.0.2.1:830 (Session ID: 45)
urn:ietf:params:netconf:base:1.0
urn:ietf:params:netconf:base:1.1
urn:ietf:params:netconf:capability:candidate:1.0
urn:ietf:params:netconf:capability:confirmed-commit:1.0
urn:ietf:params:netconf:capability:confirmed-commit:1.1
urn:ietf:params:netconf:capability:rollback-on-error:1.0
urn:ietf:params:netconf:capability:startup:1.0
urn:ietf:params:netconf:capability:url:1.0?scheme=file,ftp,http
urn:ietf:params:netconf:capability:notification:1.0
urn:ietf:params:netconf:capability:interleave:1.0
urn:ietf:params:netconf:capability:with-defaults:1.0?basic-mode=explicit&also-supported=trim,report-all,report-all-tagged
```