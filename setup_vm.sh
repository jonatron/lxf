apt-get update
apt-get -y install zfsutils-linux python3-pip libffi-dev debconf-utils
pip3 install --upgrade pip
apt-get -y install libssl-dev
pip3 install pylxd
cd /vagrant/
debconf-set-selections < lxd_debconf.conf
dpkg-reconfigure -p medium -fnoninteractive lxd
# 10GB ZFS to play around with
lxd init --auto --storage-backend=zfs --storage-create-loop=10 --storage-pool=zfs
