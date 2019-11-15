#!/bin/bashsudo

# deleting vxlan
sudo ip link set dev "$2-vx-$1" down
sudo brctl delif "$2-br" "$2-vx-$1"
sudo ip link del dev "$2-vx-$1"

# delete bridge
sudo brctl delif "$2-br" "$3"
sudo ip link del dev "$3"
sudo ip link set dev "$2-br" down
sudo brctl delbr "$2-br"

# destroy and undefine network
sudo virsh net-destroy $2
sudo virsh net-undefine $2
