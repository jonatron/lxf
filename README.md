Lxf
===
Lxf is a small python script to use the general idea of Dockerfiles with LXC/LXD.
It's just a toy at the moment. Created because sometimes you want to think about
containers as lightweight VMs rather than individual processes.

Lxffile Format
--------------

Top line:

image name eg: `ubuntu/xenial/amd64`

Next lines:

 - ADD source dest eg: `ADD fakesource /moo/`
 - command to run eg: `mkdir /srv/foo`
 - comments eg: `# hello`

Demonstration
---------------------

**[This repository has included a Vagrantfile, to make it easy to try LXF out]**

`jon lxf (master) $ vagrant up && vagrant ssh`

`ubuntu@ubuntu-xenial:/vagrant$ cat Lxffile`

```
ubuntu/xenial/amd64
apt-get update
/bin/bash -c "echo \"a1\" > a2"
ADD fakesource /moo/
/bin/bash -c "echo \"b3\" > b4"
```

**[lxf.py takes a single argument, the container name]**

`ubuntu@ubuntu-xenial:/vagrant$ ./lxf.py a1`

```
[some output removed]
key 20b17e08ab94667a
No snapshot found
Creating new Container
config: {'mode': 'pull', 'source': {'type': 'image', 'alias': 'ubuntu/xenial/amd64', 'server': 'https://images.linuxcontainers.org'}, 'name': 'a1'}
Waiting for container to boot
Trying to contact container
stdout Hit:1 http://archive.ubuntu.com/ubuntu xenial InRelease
Fetched 601 kB in 0s (1431 kB/s)
Reading package lists...
key 729936be33cf6c04
key 49ab7b3948b88104
key 5af95bee295ffc9f
```

`ubuntu@ubuntu-xenial:/vagrant$ lxc exec a1 bash`

**[check the commands have run (b4 is there)]**

`root@a1:~# ls /`

```
a2  bin   dev  home  lib64  mnt  opt   root  sbin  sys  usr
b4  boot  etc  lib   media  moo  proc  run   srv   tmp  var
```

`root@a1:~# ls /moo/fakesource/`

`moo.py  test.txt`

**[Add a line to the Lxffile]**

`ubuntu@ubuntu-xenial:/vagrant$ echo '/bin/bash -c "echo \"testing\" > testing"' >> Lxffile`

**[Create a new container, using the modified Lxffile]**

`ubuntu@ubuntu-xenial:/vagrant$ ./lxf.py a3`

**[note this creates a container from a snapshot (5af95bee295ffc9f)]**

```
all_snapshots defaultdict(<class 'list'>, {'c2b94885779b668f': ['a1'], '729936be33cf6c04': ['a1'], '5af95bee295ffc9f': ['a1'], '49ab7b3948b88104': ['a1'], '20b17e08ab94667a': ['a1']})
key 20b17e08ab94667a
key 729936be33cf6c04
key 49ab7b3948b88104
key 5af95bee295ffc9f
key 47e17d8755ddb040
Creating new Container
config: {'name': 'a3', 'source': {'source': 'a1/5af95bee295ffc9f', 'type': 'copy'}}
Waiting for container to boot
Trying to contact container
stdout
stderr
```

`ubuntu@ubuntu-xenial:/vagrant$ lxc exec a3 bash`

```
root@a3:~# ls /
root@a3:~# cat /testing
testing
```
