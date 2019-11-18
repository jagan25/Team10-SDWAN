#!/bin/bashsudo

sudo virsh destroy $1
sudo virsh undefine $1
