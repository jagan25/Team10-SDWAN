import sys
import yaml
import logging
import subprocess
import time

CONFIG_FOLDER_PATH = '/etc/config/container/'
ANSIBLE_FOLDER_PATH = '/var/scripts/container/'
SITE_NET_LIST = 'site_net_list.yaml'
NS_LIST = 'ns_list.yaml'
ASSIGN_IPROUTE = ANSIBLE_FOLDER_PATH + "assign_ip_route.yaml"

def read_yaml_data(f_name):
  data = None
  with open(f_name) as stream:
    data = yaml.safe_load(stream)
  return data

def write_yaml_data(data, f_name):
  with open(f_name, 'w') as outfile:
    yaml.dump(data, outfile)

def transit(tid, hypervisor, network, flag):
    if hypervisor == 'primary':
        if flag == 'i':
            nh = str(tid)+".0.2.1"
        else:
            nh = "gre_t"+str(tid) 
    else:
        if flag == 'i':
            nh = str(tid)+".255.2.1"
        else:
            nh = "gre_t"+str(tid)
    for n in network:
        if nh.startswith("gre"):
            command = "sudo ansible-playbook " + ASSIGN_IPROUTE + " -e hypervisor="+hypervisor+" -e option1=transit -e option2=gre -e transit_name=t"+str(tid)+"_transit -e network="+n+" -e nh="+nh
        else:
            command = "sudo ansible-playbook " + ASSIGN_IPROUTE + " -e hypervisor="+hypervisor+" -e option1=transit -e option2=normal -e transit_name=t"+str(tid)+"_transit -e network="+n+" -e nh="+nh
        print(command)
        #subprocess.call([command], shell=True)


def ce(tid, sid, hypervisor, network, flag, ce_name):
    for n in network:
        if flag == "i":
            nh = str(tid)+"."+str(sid)+".0.254"
            command = "sudo ansible-playbook " + ASSIGN_IPROUTE + " -e hypervisor="+hypervisor+" -e option1=normal -e option2=normal -e container="+ce_name +" -e network="+n+" -e nh="+nh
            print(command)
            #subprocess.call([command], shell=True)
        else:
            print(n+"via default")

def pe(tid,sid,pid, hypervisor, network, flag, pe_name):
     for n in network:
        if flag == "i":
            for i in range(len(pid)):
                if pe_name[5:] == str(pid[i]):
                    nh = str(tid)+"."+str(sid)+"."+str(pid[i])+".1"
                    command = "sudo ansible-playbook " + ASSIGN_IPROUTE + " -e hypervisor="+hypervisor+" -e option1=normal -e option2=normal -e container="+pe_name +" -e network="+n+" -e nh="+nh
                    print(command)
                #subprocess.call([command], shell=True)
        else:
            print(n + " via default")

def main():
    ns_list = read_yaml_data(CONFIG_FOLDER_PATH + NS_LIST)
    site_net_list = read_yaml_data(CONFIG_FOLDER_PATH + SITE_NET_LIST)
    
    
    for ns in ns_list['list']:
        # go inside the ns and add routes
        for nets in site_net_list['site']:
            if ns['hypervisor']=='primary':
                if nets['hypervisor']=='primary':
                    if 'transit' in ns['name']:
                        transit(50, "primary", nets['network'], "i")
                    elif 'CE' in ns['name']:
                        ce(50,nets["id"], "primary", nets['network'], "i", ns['name'])
                    elif 'PE' in ns['name']:
                        pe(50, nets["id"],nets["pid"],"primary", nets['network'], "i", ns['name'])
                else:
                    if 'transit' in ns['name']:
                        transit(50, "primary", nets['network'], "o")
                    elif 'CE' in ns['name']:
                        ce(50,nets["id"], "primary", nets['network'], "o", ns['name'])
                    elif 'PE' in ns['name']:
                        pe(50,nets["id"],nets["pid"], "primary", nets['network'], "o", ns['name'])

            else:
                if nets['hypervisor']=='primary':
                    if 'transit' in ns['name']:
                        transit(50, "secondary", nets['network'], "o")
                    elif 'CE' in ns['name']:
                        ce(50,nets["id"], "secondary", nets['network'], "o", ns['name'])
                    elif 'PE' in ns['name']:
                        pe(50,nets["id"],nets["pid"], "secondary", nets['network'], "o", ns['name'])

                else:
                    if 'transit' in ns['name']:
                        transit(50, "secondary", nets['network'], "i")
                    elif 'CE' in ns['name']:
                        ce(50,nets["id"], "secondary", nets['network'], "i", ns['name'])
                    elif 'PE' in ns['name']:
                        pe(50,nets["id"],nets["pid"], "secondary", nets['network'], "i", ns['name'])

if __name__ == '__main__':
    main()
