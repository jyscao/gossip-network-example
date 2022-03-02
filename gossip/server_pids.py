import os, json


# .server_pids.json is used by cli.py to stop the network & remove nodes
SRV_PIDS_FILE = ".srv_pids.json"


def write_pids_map_to_file(pids_map):
    with open(SRV_PIDS_FILE, "w") as f:
        f.write(json.dumps(pids_map))


def read_server_pids_to_map():
    with open(SRV_PIDS_FILE) as f:
        return json.loads(f.read())
