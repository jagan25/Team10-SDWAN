#!/bin/bashsudo

# destroy and undefine network
sudo virsh net-destroy $1
sudo virsh net-undefine $1

# delete bridge
sudo ip link set dev $2 down
sudo brctl delbr $2
