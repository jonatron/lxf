# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/xenial64"

  config.vm.network "forwarded_port", guest: 8000, host: 7777

  config.vm.provision "shell", path: "setup_vm.sh"
  config.vm.provision "shell", path: "setup_vm_unprivileged.sh", privileged: false

end
