#!/bin/bashsudo

# destroy and undefine network
sudo virsh net-destroy "$1_controller_net"
sudo virsh net-undefine "$1_controller_net"

# delete bridge
sudo ip link set dev "$1_controllerbr" down
sudo brctl delbr "$1_controllerbr"

# delete vxlan interface
sudo ip link set dev "$1-vxlan" down
sudo ip link del dev "$1-vxlan"

# delete vethpair transit -- cntroller
sudo ip link set dev "veth_$1c2t" down
sudo ip link del dev "veth_$1c2t"

