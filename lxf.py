#!/usr/bin/env python3

import hashlib
import shlex
import subprocess
import sys
import time
from collections import defaultdict

from pylxd.client import Client
from pylxd import exceptions


def short_md5(thing):
    return hashlib.md5(thing).hexdigest()[:16]


lxd = Client()


with open('Lxffile', 'r') as f:
    lxffile = f.read()

lines = lxffile.splitlines()


def create_container(name, snapshot_name=None):
    try:
        cntr = lxd.containers.get(name)
    except (NameError, exceptions.LXDAPIException):
        print("Creating new Container")
    else:
        print("Container already exists...")
        return cntr
    print("snapshot_name cc", repr(snapshot_name))
    if snapshot_name:
        config = {
            "name": name,
            "source": {
                "type": "copy",
                "source": snapshot_name,
            }
        }
    else:
        config = {
            "name": name,
            "mode": "pull",
            "source": {
                "type": "image",
                "alias": lines[0],
                "server": "https://images.linuxcontainers.org",
            }
        }
    print("config:", config)
    cntr = lxd.containers.create(config, wait=True)
    cntr.start()
    for i in range(10):
        if i == 9:
            raise Exception("Failed to create container")
        try:
            cntr.state().network['eth0']['addresses'][0]['address']
        except TypeError:
            print("Waiting for container to boot")
            time.sleep(1)
            continue
        break
    time.sleep(5)  # still needs some extra time
    return cntr


all_containers = lxd.containers.all()
all_snapshots = defaultdict(list)
for cont in all_containers:
    for s in cont.snapshots.all():
        all_snapshots[s.name].append(cont.name)

print("all_snapshots", all_snapshots)

try:
    name = sys.argv[1]
except IndexError:
    raise Exception("Specify a container name")


cntr = None
lines_up_to_here = ""
last_key = None
snapshot_name = None
for i, line in enumerate(lines):
    if i == 0:
        continue
    lines_up_to_here += line
    if line.startswith("ADD"):
        files, dest = shlex.split(line[4:])
        try:
            tar_output = subprocess.check_output(["tar", "-cf", "/tmp/lxf.tar", files])
        except subprocess.CalledProcessError:
            raise Exception("ADD File does not exist", line)
        md5sum_out = subprocess.check_output(["md5sum", "/tmp/lxf.tar"])
        md5sum = md5sum_out.split(b" ")[0].strip()
        if len(md5sum) != 32:
            raise Exception("Something went wrong with: ", line)
        key = md5sum[:16].decode("utf-8")
    else:
        key = short_md5(lines_up_to_here.encode('utf-8'))
    print("key", key)
    if key not in all_snapshots:
        if not cntr:
            try:
                snapshot_name = all_snapshots[last_key][0] + "/" + last_key
            except (IndexError, KeyError):
                print("No snapshot found")
                snapshot_name = None
            cntr = create_container(name, snapshot_name)
        if line.startswith("ADD"):  # todo move to before key is generated
            cntr.execute(['mkdir', dest])
            target = cntr.name + "//tmp/lxf.tar"
            push_output = subprocess.check_output(["lxc", "file", "push", "/tmp/lxf.tar", target])
            cntr.execute(['tar', '-xf', '/tmp/lxf.tar', '-C', dest])
            cntr.execute(['rm', '/tmp/lxf.tar'])
        else:
            stdout, stderr = cntr.execute(shlex.split(line))
            print("stdout", stdout)
            print("stderr", stderr)
        cntr.snapshots.create(key, wait=True)
    last_key = key
if not cntr:
    try:
        snapshot_name = all_snapshots[last_key][0] + "/" + last_key
    except IndexError:
        snapshot_name = None
    cntr = create_container(name, snapshot_name)
