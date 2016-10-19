apt-get update
apt-get -y install zfsutils-linux python3-pip libffi-dev debconf-utils
pip3 install --upgrade pip
apt-get -y install libssl-dev
pip3 install pylxd
cd /vagrant/
cp default-lxd-bridge-copy /etc/default/lxd-bridge
service lxd-bridge restart
service lxd restart
# 10GB ZFS to play around with
lxd init --auto --storage-backend=zfs --storage-create-loop=10 --storage-pool=zfs
lxc list
echo "cd /vagrant/" >> /home/ubuntu/.bashrc
