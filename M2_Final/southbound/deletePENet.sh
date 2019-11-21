#!/bin/bashsudo

# destroy and undefine network
sudo virsh net-destroy "$1_PEnet"
sudo virsh net-undefine "$1_PEnet"

# delete bridge
sudo ip link set dev "$1_PEnet" down
sudo brctl delbr "$1_PEnet"

# delete veth pair to transit
sudo ip link set dev "$1PEveth" down
sudo ip link del dev "$1PEveth"
