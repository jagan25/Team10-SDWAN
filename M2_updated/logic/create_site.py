import sys
import yaml
import logging
import subprocess

def createFunc(yFile,yFileName):
    print("create")
    hypervisor = yFile['tenant']['hypervisor']
    ns_name = yFile['tenant']['tenant_name']+yFile['tenant']['site']
    if yFile['tenant']['change_ns'].lower()=='y':
        # playbook to create NS
        command = 'sudo ansible-playbook /var/scripts/create_ns.yaml -e hypervisor='+hypervisor+' -e ns_name='+ns_name+' -e hypervisorIP='+yFile['tenant']['site_ip_ext']+' -e transitIP='+yFile['tenant']['site_ip_int']
        subprocess.call([command],shell=True)

    # playbook to create networks
    if yFile['tenant']['change_net'].lower()=='y':
        for net in yFile['tenant']['networks']:
            net_name = ns_name+net
            command = 'sudo ansible-playbook /var/scripts/create_l2net.yaml -e hypervisor='+hypervisor+' -e bridge_name='+net_name+' -e network_name='+net_name
            subprocess.call([command],shell=True)
            
            # playbook to attach network bridges to namespace
            veth1 = str(yFile['tenant']['tenant_id'])+'_'+str(yFile['tenant']['site_id'])+'_'+net+'1'
            veth2 = str(yFile['tenant']['tenant_id'])+'_'+str(yFile['tenant']['site_id'])+'_'+net+'2'
            command = 'sudo ansible-playbook /var/scripts/create_brns_conn.yaml -e hypervisor='+hypervisor+" -e veth1="+veth1+" -e veth2="+veth2+" -e bridge_name="+net_name+" -e namespace="+ns_name
            subprocess.call([command],shell=True)

    # playbook to create vms
    if yFile['tenant']['change_vm'].lower()=='y':
        for vm in yFile['router']:
            command = "sudo ansible-playbook /var/scripts/create_vm.yaml -e hypervisor=" + hypervisor +" -e vm_name="+str(vm['name']) +" -e mem="+str(vm['mem'])+" -e vcpu="+str(vm['vcpu']) +" -e network="+ns_name+vm['networks'][0]
            subprocess.call([command],shell=True)
            
            # playbook to attach to other networks
            if len(vm['networks'])>1:
                for i in range(1,len(vm['networks'])):
                    command = "sudo ansible-playbook /var/scripts/create_conn.yaml -e vm="+vm['name']+" -e network="+ns_name+vm['networks'][i]+ " -e hypervisor="+yFile['hypervisorType']
                    subprocess.call([command], shell = True)

def deleteFunc(yFile,yFileName):
    print("delete")
    hypervisor = yFile['tenant']['hypervisor']
    ns_name = yFile['tenant']['tenant_name']+yFile['tenant']['site']
    # playbook to delete NS
    if yFile['tenant']['change_ns'].lower()=='y':
        command = 'sudo ansible-playbook /var/scripts/delete_ns.yaml -e hypervisor='+hypervisor+' -e ns_name='+ns_name
        subprocess.call([command],shell=True)

    # playbook to delete networks
    if yFile['tenant']['change_net'].lower()=='y':
        for net in yFile['tenant']['networks']:
            net_name = ns_name+net
            command = 'sudo ansible-playbook /var/scripts/delete_l2net.yaml -e hypervisor='+hypervisor+' -e bridge_name='+net_name+' -e network_name='+net_name
            subprocess.call([command],shell=True)

            # playbook to delete veth pair bridge and namespace
            veth1 = str(yFile['tenant']['tenant_id'])+'_'+str(yFile['tenant']['site_id'])+'_'+net+'1'
            command = 'sudo ansible-playbook /var/scripts/delete_brns_conn.yaml -e hypervisor='+hypervisor+" -e veth1="+veth1
            subprocess.call([command],shell=True)

    # playbook to delete vms
    if yFile['tenant']['change_vm'].lower()=='y':
        for vm in yFile['router']:
            command = "sudo ansible-playbook /var/scripts/delete_vm.yaml -e hypervisor=" + hypervisor +" -e vm_name="+str(vm['name'])
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
            #open the yaml file
            with open(yFileName,'r') as file:
                yFile = yaml.load(file)
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
