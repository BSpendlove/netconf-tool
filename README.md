# netconf-tool

This is a tool aimed for developer experience / making things faster when I am trying to test NETCONF related tasks without having to rewrite a random python script. I've found myself constantly writing little python scripts for NETCONF to test functionality or even grab data such as server capabilities, setup event based notifications/subscription to test something and have probably got 100 scripts that do the same thing in different folders through the various projects I've worked on.

Therefore I've created this tool to improve my developer experience working with NETCONF. At the ease of a quick command, I want to be able to get config, try out some edit-config functionality, grab capabilities of a new vendor I am working with, test NETCONF notifications etc... and now I can and want to share my progress as I work my way through adding functionality to this tool.

Here are the reasons for the required modules:

- ncclient                  - Obvious one... Handles the low networking level of SSH/NETCONF
- click and click-plugins   - Click is an awesome tool to build CLI applications, netconf-tool is a CLI application
- loguru                    - Best logging module out there, I don't like exit() and print() statements...
- redis                     - Used to test notification events against a redis pubsub environment
- pika                      - Used to test notification events against a rabbitmq environment
- xmltodict                 - Allow lazy conversion from XML to JSON for formatting arguments on some commands

This CLI application is built to load plugins using the entrypoint of netconf-tools so I may look into adding more functionality once I move over all my developer focused NETCONF tasks to this CLI project.

The plan in the future is to setup a better experience for contributers with pytest and a better pipeline however I will try my best not to break everything when I release a new version...

## Environment Variables

Use NETCONF_TOOL_USERNAME and NETCONF_TOOL_PASSWORD environment variables to prevent exposing the --username and --password arguments in your operating system CLI history.

## Feature Examples

### netconf-tool subscription local

This creates a notification event subscription (RFC 5277) and displays the NETCONF payload on the screen, currently doesn't support replay functionality but is useful when developing NETCONF based alerting NMS/applications.

```bash
$ netconf-tool subscription local --host 192.0.2.1
2023-04-28 22:12:14.299 | INFO     | netconf_tool.subscription.local:cli_subscription_local:18 - Attempting to establish NETCONF session to 192.0.2.1:830
2023-04-28 22:12:14.662 | SUCCESS  | netconf_tool.subscription.local:cli_subscription_local:28 - Established NETCONF connection to 192.0.2.1:830 (Session ID: 43)
2023-04-28 22:12:14.770 | SUCCESS  | netconf_tool.subscription.local:cli_subscription_local:32 - Created Netconf Subscription, you can exit out of here using Ctrl+C
2023-04-28 22:12:14.770 | INFO     | netconf_tool.subscription.local:cli_subscription_local:38 - Awaiting next NETCONF <notification/>
2023-04-28 22:12:23.035 | INFO     | netconf_tool.subscription.local:cli_subscription_local:41 - <?xml version="1.0" encoding="UTF-8"?>
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

### netconf-tool subscription redis-pubsub

Similar to `netconf-tool subscription local` however sends the NETCONF notification/event to a Redis pubsub channel.

```bash
$ netconf-tool subscription redis-pubsub --host 192.0.2.1
2023-04-29 17:32:55.350 | INFO     | netconf_tool.subscription.redis:cli_subscription_redis_pubsub:35 - Checking if Redis server 127.0.0.1:6379 is available
2023-04-29 17:32:55.374 | SUCCESS  | netconf_tool.subscription.redis:cli_subscription_redis_pubsub:39 - Redis server is available...
2023-04-29 17:32:55.374 | INFO     | netconf_tool.subscription.redis:cli_subscription_redis_pubsub:44 - Attempting to establish NETCONF session to 192.0.2.1:830
2023-04-29 17:32:55.725 | SUCCESS  | netconf_tool.subscription.redis:cli_subscription_redis_pubsub:55 - Established NETCONF connection to 192.0.2.1:830 (Session ID: 117)
2023-04-29 17:32:55.832 | SUCCESS  | netconf_tool.subscription.redis:cli_subscription_redis_pubsub:59 - Created Netconf Subscription, you can exit out of here using Ctrl+C
2023-04-29 17:32:55.833 | INFO     | netconf_tool.subscription.redis:cli_subscription_redis_pubsub:65 - Awaiting next NETCONF <notification/>
```

Example using redis-cli
```
$ redis-cli
127.0.0.1:6379> subscribe netconf_tool:all_events
Reading messages... (press Ctrl-C to quit)
1) "subscribe"
2) "netconf_tool:all_events"
3) (integer) 1
1) "message"
2) "netconf_tool:all_events"
3) "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<notification xmlns=\"urn:ietf:params:xml:ns:netconf:notification:1.0\">\n  <eventTime>2023-04-29T15:24:39Z</eventTime>\n  <netconf-config-change xmlns=\"urn:ietf:params:xml:ns:yang:ietf-netconf-notifications\">\n    <changed-by>\n      <username>netconftool</username>\n      <session-id>0</session-id>\n    </changed-by>\n    <datastore>running</datastore>\n    <edit>\n      <target\n        xmlns:oc-if=\"http://openconfig.net/yang/interfaces\">/oc-if:interfaces/oc-if:interface[name='xe7']/oc-if:config</target>\n      <operation>merge</operation>\n    </edit>\n    <edit>\n      <target\n        xmlns:oc-netinst=\"http://openconfig.net/yang/network-instance\">/oc-netinst:network-instances/oc-netinst:network-instance/oc-netinst:interfaces/oc-netinst:interface</target>\n      <operation>merge</operation>\n    </edit>\n  </netconf-config-change>\n</notification>"
1) "message"
2) "netconf_tool:all_events"
3) "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<notification xmlns=\"urn:ietf:params:xml:ns:netconf:notification:1.0\">\n  <eventTime>2023-04-29T15:24:39Z</eventTime>\n  <severity>critical</severity>\n  <eventClass>state</eventClass>\n  <interface-link-state-change-notification xmlns=\"http://www.ipinfusion.com/yang/ocnos/ipi-interface\">\n    <name>xe7</name>\n    <oper-status>down</oper-status>\n  </interface-link-state-change-notification>\n</notification>"
```

### netconf-tool subscription rabbitmq

Similar to `netconf-tool subscription local` however sends the NETCONF notification/event to a RabbitMQ Queue.

```bash
$ netconf-tool subscription rabbitmq --host 192.0.2.1
2023-04-29 17:35:35.465 | INFO     | netconf_tool.subscription.rabbitmq:cli_subscription_rabbitmq:78 - Checking if RabbitMQ Server 127.0.0.1:5672 is available
2023-04-29 17:35:35.465 | INFO     | netconf_tool.subscription.rabbitmq:cli_subscription_rabbitmq:82 - Attempting to establish NETCONF session to 192.0.2.1:830
2023-04-29 17:35:35.831 | SUCCESS  | netconf_tool.subscription.rabbitmq:cli_subscription_rabbitmq:92 - Established NETCONF connection to 192.0.2.1:830 (Session ID: 118)
2023-04-29 17:35:35.938 | SUCCESS  | netconf_tool.subscription.rabbitmq:cli_subscription_rabbitmq:96 - Created Netconf Subscription, you can exit out of here using Ctrl+C
2023-04-29 17:35:35.938 | INFO     | netconf_tool.subscription.rabbitmq:cli_subscription_rabbitmq:102 - Awaiting next NETCONF <notification/>
```

### netconf-tool operations get-config

Simply prints out the returned data using the `get-config` NETCONF operation.

```bash
$ netconf-tool operations get-config --host 192.0.2.1
2023-04-29 17:28:48.547 | INFO     | netconf_tool.operations.get_config:cli_operations_get_config:43 - Attempting to establish NETCONF session to 192.0.2.1:830
2023-04-29 17:28:48.915 | SUCCESS  | netconf_tool.operations.get_config:cli_operations_get_config:53 - Established NETCONF connection to 192.0.2.1:830 (Session ID: 115)
<?xml version="1.0" ?><data xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
<ommited>
```

### netconf-tool operations list-server-capabilities

Prints the server capabilities unless --export-json flag is used, if this flag is used then each capability will be parsed into an RFC3986 compliant object/dictionary and then exported into the relevant filename used in this argument.

```bash
$ netconf-tool operations list-server-capabilities --host 192.0.2.1
2023-04-29 17:27:59.209 | INFO     | netconf_tool.operations.capabilities:netconf_tool_cli_operations_list_server_capabilities:29 - Attempting to establish NETCONF session to 192.0.2.1:830
2023-04-29 17:27:59.566 | SUCCESS  | netconf_tool.operations.capabilities:netconf_tool_cli_operations_list_server_capabilities:39 - Established NETCONF connection to 192.0.2.1:830 (Session ID: 113)
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

### netconf-tool yangcli get-config

This command will attempt to lazily build the dynamic XML filter for a provided command in the traditional CLI style, it was inspired by yangcli however doesn't involve YANG at all for any validation, its simply a hack to build the filter if you have an idea of the XML format without having to wrap the text in XML tags. For example if you are trying to just pull the overload-bit configuration from ISIS using Openconfig, then format your CLI command like this:

`network-instances@http://openconfig.net/yang/network-instance network-instance protocols protocol isis global lsp-bit overload-bit config`

Use `@` to include XML Namespaces in your command structure. This simply sets the XML name of the element to` xmlns` and uses the value after the @.

```
netconf-tool yangcli get-config --host 192.0.2.1 "network-instances@http://openconfig.net/yang/network-instance network-instance protocols protocol isis global lsp-bit overload-bit config"
2023-04-29 17:40:44.033 | DEBUG    | netconf_tool.yangcli.get_config:netconf_tool_cli_yangcli_get_config:38 - Filter that will be used for get-config: <network-instances xmlns="http://openconfig.net/yang/network-instance"><network-instance><protocols><protocol><isis><global><lsp-bit><overload-bit><config /></overload-bit></lsp-bit></global></isis></protocol></protocols></network-instance></network-instances>
2023-04-29 17:40:44.034 | INFO     | netconf_tool.yangcli.get_config:netconf_tool_cli_yangcli_get_config:39 - Attempting to establish NETCONF session to 192.0.2.1:830
2023-04-29 17:40:47.916 | SUCCESS  | netconf_tool.yangcli.get_config:netconf_tool_cli_yangcli_get_config:50 - Established NETCONF connection to 192.0.2.1:830 (Session ID: 22532404)
<?xml version="1.0" ?><data xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0"> 
   <network-instances xmlns="http://openconfig.net/yang/network-instance">  
     <network-instance>   
       <name>default</name>   
       <protocols>    
         <protocol>     
           <identifier xmlns:idx="http://openconfig.net/yang/policy-types">idx:ISIS</identifier>     
           <name>1</name>     
           <isis>      
             <global>       
               <lsp-bit>        
                 <overload-bit>         
                   <config>          
                     <set-bit-on-boot>true</set-bit-on-boot>          
                   </config>         
                 </overload-bit>        
               </lsp-bit>       
             </global>      
           </isis>     
         </protocol>    
       </protocols>   
     </network-instance>  
   </network-instances> 
 </data>
```

### netconf-tool operations get-yang-models

Gathers all YANG models present on the NETCONF server and saves them by default to `./yang_models`

```
$ netconf-tool operations get-yang-models --host 192.0.2.1
2023-05-01 08:34:24.603 | INFO     | netconf_tool.operations.get_yang:cli_operations_get_yang_models:36 - Attempting to establish NETCONF session to 192.0.2.1:830
2023-05-01 08:34:24.965 | SUCCESS  | netconf_tool.operations.get_yang:cli_operations_get_yang_models:46 - Established NETCONF connection to 192.0.2.1:830 (Session ID: 164)
2023-05-01 08:34:49.831 | SUCCESS  | netconf_tool.operations.get_yang:cli_operations_get_yang_models:62 - Exported module nc-notifications (yang_models/nc-notifications.yang)
2023-05-01 08:34:49.938 | SUCCESS  | netconf_tool.operations.get_yang:cli_operations_get_yang_models:62 - Exported module notifications (yang_models/notifications.yang)
2023-05-01 08:34:50.046 | SUCCESS  | netconf_tool.operations.get_yang:cli_operations_get_yang_models:62 - Exported module openconfig-aaa (yang_models/openconfig-aaa.yang)
2023-05-01 08:34:50.154 | SUCCESS  | netconf_tool.operations.get_yang:cli_operations_get_yang_models:62 - Exported module openconfig-aaa-types (yang_models/openconfig-aaa-types.yang)
2023-05-01 08:34:50.262 | SUCCESS  | netconf_tool.operations.get_yang:cli_operations_get_yang_models:62 - Exported module openconfig-acl (yang_models/openconfig-acl.yang)
2023-05-01 08:34:50.369 | SUCCESS  | netconf_tool.operations.get_yang:cli_operations_get_yang_models:62 - Exported module openconfig-aft (yang_models/openconfig-aft.yang)
2023-05-01 08:34:50.476 | SUCCESS  | netconf_tool.operations.get_yang:cli_operations_get_yang_models:62 - Exported module openconfig-aft-types (yang_models/openconfig-aft-types.yang)
2023-05-01 08:34:50.583 | SUCCESS  | netconf_tool.operations.get_yang:cli_operations_get_yang_models:62 - Exported module openconfig-alarm-types (yang_models/openconfig-alarm-types.yang)
2023-05-01 08:34:50.690 | SUCCESS  | netconf_tool.operations.get_yang:cli_operations_get_yang_models:62 - Exported module openconfig-alarms (yang_models/openconfig-alarms.yang)
............. and so on .............
2023-05-01 08:37:21.411 | SUCCESS  | netconf_tool.operations.get_yang:cli_operations_get_yang_models:76 - Exported a total of 280 YANG models
```

### netconf-tool operations get-yang-model

Gathers a specific YANG model if it exist on the NETCONF server and saves it by default to `./yang_models`

```
$ netconf-tool operations get-yang-model --host 192.0.2.1 --name openconfig-segment-routing
2023-05-01 08:31:21.036 | INFO     | netconf_tool.operations.get_yang:cli_operations_get_yang_model:96 - Creating output directory and any child folders
2023-05-01 08:31:21.036 | INFO     | netconf_tool.operations.get_yang:cli_operations_get_yang_model:100 - Attempting to establish NETCONF session to 192.0.2.1:830
2023-05-01 08:31:21.398 | SUCCESS  | netconf_tool.operations.get_yang:cli_operations_get_yang_model:110 - Established NETCONF connection to 192.0.2.1:830 (Session ID: 162)
2023-05-01 08:31:21.508 | SUCCESS  | netconf_tool.operations.get_yang:cli_operations_get_yang_model:134 - Exported module openconfig-segment-routing (yang_models/openconfig-segment-routing.yang)
```