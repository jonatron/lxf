#!/usr/bin/env python3

import hashlib
import sys
import shlex
import time
from pylxd.client import Client
from pylxd import exceptions


def md5(thing):
    return hashlib.md5(thing).hexdigest()


lxd = Client()


with open('Lxcfile', 'r') as f:
    lxcfile = f.read()

lines = lxcfile.splitlines()


def create_container(name):
    config = {
        "name": name,
        "mode": "pull",
        "source": {
            "type": "image",
            "alias": lines[0],
            "server": "https://images.linuxcontainers.org",
        }
    }
    cont = lxd.containers.create(config, wait=True)
    cont.start()
    for i in range(10):
        try:
            cont.state().network['eth0']['addresses'][0]['address']
        except TypeError:
            print("Waiting for container to boot")
            time.sleep(1)
            continue
        break
    time.sleep(2)  # still needs some extra time
    return cont


try:
    name = sys.argv[1]
except IndexError:
    raise Exception("Specify a container name")
else:
    try:
        cont = lxd.containers.get(name)
        print("Container already exists, skipping...")
    except (NameError, exceptions.LXDAPIException):
        cont = create_container(name)
print("name", name)


lines_up_to_here = ""
for i, line in enumerate(lines):
    if i == 0:
        continue
    lines_up_to_here += line
    key = md5(lines_up_to_here.encode('utf-8'))[:16]
    snapshot_names = [c.name for c in cont.snapshots.all()]
    print("snapshot_names", snapshot_names)
    if key not in snapshot_names:
        print("key not in snapshot_names", key)
        print("executing line", line)
        stdout, stderr = cont.execute(shlex.split(line))
        cont.snapshots.create(key, wait=True)
        print("stdout", stdout)
        print("stderr", stderr)
