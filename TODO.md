# TODO List


## Main Tasks
- [x] connect via TCP
- [x] implement send-message
- [x] implement get-messages
- [x] use message + destination node + time to uniquely identify each sent message
- [x] update relevant peers on remove-node


## Important Miscellanea
- [x] create graph visualization of connected nodes
- [ ] add type hints to all functions & methods
- [ ] use black & flake8 to format code
- [ ] add `--ports-origin` option to allow specifying originating port number from CLI (to allow multiple independent networks to be started simultaneously)
- [ ] related to above: add commands handlers to server to respond to queries about PORTS_ORIGIN & server PID (removes .srv_pids.json file)
- [ ] reconfigure network connection on remove-node -> if a node has all its peers removed, randomly connect it to new peers -> or create command to allow reconnection to new neighbor


## Nice Touches
- [x] show all routes/paths message took to reach node (also show shortest & longest routes?)
- [x] add get-unread-messages & get-read-messages commands (determined by get-messages)
- [x] show message origination time
- [ ] add optional depth of connectedness to list-peers client command
- [ ] use Trio to allow async send-message commands
- [ ] color nodes differently & also use those same colors when printing node IDs to the console
- [ ] add restructure-network commands (re-connect nodes randomly), with optional args: min & max connections
