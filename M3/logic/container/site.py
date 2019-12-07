import sys
import yaml
import logging
import subprocess

CONFIG_FOLDER_PATH = '/etc/config/container/'
ANSIBLE_FOLDER_PATH = '/var/scripts/container/'
CREATE_NS_SCRIPT = ANSIBLE_FOLDER_PATH+"create_ns.yaml"
CREATE_L2_BRIDGE_SCRIPT = ANSIBLE_FOLDER_PATH+"create_l2net.yaml"
CREATE_BRNS_CONN_SCRIPT = ANSIBLE_FOLDER_PATH+"create_brns_conn.yaml"
CREATE_CONTAINER_SCRIPT = ANSIBLE_FOLDER_PATH+"create_container.yaml"
CREATE_DOC_CONN_SCRIPT = ANSIBLE_FOLDER_PATH+"create_doc_conn.yaml"
DELETE_NS_SCRIPT = ANSIBLE_FOLDER_PATH+"delete_ns.yaml"
DELETE_L2_BRIDGE_SCRIPT = ANSIBLE_FOLDER_PATH+"delete_l2net.yaml"
DELETE_BRNS_CONN_SCRIPT = ANSIBLE_FOLDER_PATH+"delete_brns_conn.yaml"
DELETE_CONTAINER_SCRIPT = ANSIBLE_FOLDER_PATH+"delete_container.yaml"

def read_yaml_data(f_name):
  data = None
  with open(f_name) as stream:
    data = yaml.safe_load(stream)
  return data

def write_yaml_data(data, f_name):
  with open(f_name, 'w') as outfile:
    yaml.dump(data, outfile)

def createFunc(yFile,yFileName):
    print("create")
    hypervisor = yFile['tenant']['hypervisorType']
    ns_name = yFile['tenant']['tenant_name']+yFile['tenant']['site']
    if yFile['tenant']['change_site'].lower()=='y':
        # playbook to create NS
        print("Creating site namespace")
        interface = []
        for i in range(len(yFile['tenant']['networks'])):
            interface.append(ns_name+'net'+str(i)+'2')
        command = 'sudo ansible-playbook ' + CREATE_NS_SCRIPT + ' -e hypervisor='+hypervisor+' -e option=dnsmasq --extra-vars "{"interface":'+str(interface)+'}" --extra-vars "{"ip_range":'+str(yFile['tenant']['networks'])+'}" -e ns_name='+ns_name+' -e hypervisorIP='+yFile['tenant']['site_ip_ext']+' -e transitIP='+yFile['tenant']['site_ip_int']
        subprocess.call([command],shell=True)

        # Create Customer Egde router's bridge
        print("Creating CE network")
        bridge = yFile['tenant']['tenant_name']+yFile['tenant']['site']+'CE_net'
        command = "sudo ansible-playbook "+ CREATE_L2_BRIDGE_SCRIPT + " -e hypervisor="+ hypervisor+" -e option=none -e bridge_name="+bridge+ " -e network_name=" +bridge
        subprocess.call([command],shell=True)

        veth1 = yFile['tenant']['tenant_name']+yFile['tenant']['site']+'CE1'
        veth2 = yFile['tenant']['tenant_name']+yFile['tenant']['site']+'CE2'
        #Connect site to CE's bridge
        print("Connecting CE network to site namespace")
        command = "sudo ansible-playbook "+ CREATE_BRNS_CONN_SCRIPT+ " -e hypervisor="+hypervisor+ " -e veth1="+veth1+" -e veth2="+veth2+" -e bridge_name="+bridge+" -e namespace="+ns_name+" -e option=assign_ip -e ip="+str(yFile['tenant']['tenant_id'])+"."+str(yFile['tenant']['site_id'])+".0.254/24"
        subprocess.call([command],shell=True)

        for p in yFile['tenant']['PE']:
            # Create bridges for each PE
            print("Creating PE network for site")
            bridge = yFile['tenant']['tenant_name']+yFile['tenant']['site']+'PE'+str(p)
            command = "sudo ansible-playbook "+CREATE_L2_BRIDGE_SCRIPT+ " -e hypervisor="+hypervisor+ " -e option=none -e bridge_name="+bridge+ " -e network_name="+bridge
            subprocess.call([command],shell=True)
            
            #Connect bridge to PE
            print("Connecting PE network to PE")
            veth1 = yFile['tenant']['tenant_name']+yFile['tenant']['site']+'PE'+str(p)+'1'
            veth2 = yFile['tenant']['tenant_name']+yFile['tenant']['site']+'PE'+str(p)+'2'
            command = "sudo ansible-playbook "+ CREATE_DOC_CONN_SCRIPT+ " -e hypervisor="+hypervisor+ " -e option=none -e option2=none -e veth1="+veth1+" -e veth2="+veth2+" -e bridge_name="+bridge+" -e container="+yFile['tenant']['tenant_name']+"PE"+str(p)+" -e option=assign_ip -e ip="+str(yFile['tenant']['tenant_id'])+"."+str(yFile['tenant']['site_id'])+"."+str(p)+".254/24"
            subprocess.call([command],shell=True)

    # playbook to create networks
    if yFile['tenant']['change_net'].lower()=='y':
        for net in range(len(yFile['tenant']['networks'])):
            net_name = ns_name+'net'+str(net)
            print("Creating network inside the site")
            command = 'sudo ansible-playbook ' + CREATE_L2_BRIDGE_SCRIPT + ' -e hypervisor='+hypervisor+' -e option=none -e bridge_name='+net_name+' -e network_name='+net_name
            subprocess.call([command],shell=True)
 #           logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Creating  L2 Bridge  : " + command + "\n")
            
            # playbook to attach network bridges to namespace
            veth1 = net_name+'1'
            veth2 = net_name+'2'
            print("Connecting network to the site namespace")
            command = 'sudo ansible-playbook ' + CREATE_BRNS_CONN_SCRIPT + ' -e hypervisor='+hypervisor+" -e veth1="+veth1+" -e veth2="+veth2+" -e bridge_name="+net_name+" -e namespace="+ns_name+ " -e option=assign_ip -e ip="+str(yFile['tenant']['site_id'])+'.0.'+str(net)+'.254/24'
            subprocess.call([command],shell=True)
  #          logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Creating  Bridge to namespace connection  : " + command + "\n")

    # playbook to create container
    if yFile['tenant']['change_container'].lower()=='y':
        for c in yFile['router']:
            container = ns_name+'router'+str(c['container_id'])
            print("Creating router container inside namespace")
            command = "sudo ansible-playbook " + CREATE_CONTAINER_SCRIPT + " -e hypervisor=" + hypervisor +" -e container="+container + " -e image="+c['image']
            subprocess.call([command],shell=True)
   #         logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Creating Customer Edge Container : " + command  + "\n")
            
            # playbook to attach to other networks
            if len(c['networks'])>0:
                for i in range(len(c['networks'])):
                    # attach provider edge to Bridge Network
                    print("Connecting router container to network")
                    net_name = ns_name+'net'+str(c['networks'][i])
                    veth1 = net_name+'r'+str(c['container_id'])+'1'
                    veth2 = net_name+'r'+str(c['container_id'])+'2'
                    command = "sudo ansible-playbook " + CREATE_DOC_CONN_SCRIPT + " -e hypervisor=" + hypervisor + " -e option=none -e option2=none -e veth1=" +veth1+ " -e veth2="+veth2+" -e bridge_name="+net_name + " -e container=" + container+" -e option=assign_ip -e ip="+str(yFile['tenant']['site_id'])+'.0.'+str(c['networks'][i])+'.'+str(c['container_id'])+'/24'
                    subprocess.call([command],shell=True)
    #                logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Connecting Container to bridge network : " + command  + "\n")
                    
def deleteFunc(yFile,yFileName):
    print("delete")
    hypervisor = yFile['tenant']['hypervisorType']
    ns_name = yFile['tenant']['tenant_name']+yFile['tenant']['site']
    # Deleting the site
    if yFile['tenant']['change_site'].lower()=='y':
        for c in yFile['router']:
            container = ns_name+'router'+str(c['container_id'])
            delete_container(hypervisor, container)
        for net in yFile['tenant']['networks']:
            net_name = ns_name+'net'+str(net)
            veth = net_name+'1'
            delete_net(hypervisor, net_name, net_name)
            delete_vethpair(hypervisor, veth)
        delete_ns(hypervisor, ns_name)
        bridge = yFile['tenant']['tenant_name']+yFile['tenant']['site']+'CE_net'
        delete_net(hypervisor, bridge, bridge)
        for p in yFile['tenant']['PE']:
           bridge = yFile['tenant']['tenant_name']+yFile['tenant']['site']+'PE'+str(p)
           delete_net(hypervisor, bridge, bridge)
        
    else: 
        if yFile['tenant']['change_container'].lower()=='y':
            for c in yFile['router']:
                container = ns_name+'router'+str(c['container_id'])
                delete_container(hypervisor, container)

        else:
            for c in yFile['router']:
                if c['change_link'].lower()=='y':
                    for net in c['networks']:
                        net_name = ns_name+'net'+str(net)
                        veth1 = net_name+'r'+str(c['container_id'])+'1'
                        delete_vethpair(hypervisor, veth1)

        if yFile['tenant']['change_net'].lower()=='y':
            for net in yFile['tenant']['networks']:
                net_name = ns_name+'net'+str(net)
                veth = net_name+'1'
                delete_net(hypervisor, net_name, net_name)
                delete_vethpair(hypervisor, veth)
                for c in yFile['router']:
                    if net in c['networks']:
                        veth1 = net_name+'r'+str(c['container_id'])+'1'
                        delete_vethpair(hypervisor, veth1)

def delete_ns(hypervisor, ns_name):
    command = 'sudo ansible-playbook ' + DELETE_NS_SCRIPT + ' -e hypervisor='+hypervisor+' -e ns_name='+ns_name
    subprocess.call([command],shell=True)

def delete_net(hypervisor, bridge_name, network_name):
    command = 'sudo ansible-playbook ' + DELETE_L2_BRIDGE_SCRIPT + ' -e hypervisor='+hypervisor+' -e option=none -e bridge_name='+bridge_name+' -e network_name='+network_name
    subprocess.call([command],shell=True)

def delete_container(hypervisor, container):
    command = "sudo ansible-playbook " + DELETE_CONTAINER_SCRIPT + " -e hypervisor=" + hypervisor +" -e container="+container
    subprocess.call([command],shell=True)

def delete_vethpair(hypervisor, veth):
    command = 'sudo ansible-playbook ' + DELETE_BRNS_CONN_SCRIPT + ' -e hypervisor='+hypervisor+" -e veth1="+veth
    subprocess.call([command],shell=True)

def checkYAML(yaml):
    if 'tenant' not  in yaml:
        print("ERROR!!! Not in correct format!!!")
        exit(0)


if(len(sys.argv)<2):
    logging.error("\nERROR: less than 2 arguments given!!! Require 2 arguments to run")
    exit(0)
else:
    yFileName = sys.argv[2]
    # check if yaml file is passed
    if yFileName.endswith(".yml") or yFileName.endswith(".yaml"):
        try:
            yFile = read_yaml_data(CONFIG_FOLDER_PATH + yFileName)
            checkYAML(yFile)
            # check for the 1st argument i.e., create or delete
            if str(sys.argv[1]).lower()=="delete":
                print("\nPerforming delete operation depending upon the file")
                deleteFunc(yFile,yFileName)
            elif str(sys.argv[1]).lower()=="create":
                logging.info("\nPerforming create operation depending upon the file")
                createFunc(yFile,yFileName)
            else:
                logging.error("\nERROR: Unrecognized Command!!!")
                exit(0)
        except Exception as ex:
            logging.error(str(ex))
            exit(0)
    else:
        logging.error("\nERROR: No yaml/yml file found!!!")
        exit(0)

