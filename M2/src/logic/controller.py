import sys
import yaml
import logging
import subprocess
import time

CONFIG_FOLDER_PATH = '/etc/config/'
ANSIBLE_FOLDER_PATH = '/var/scripts/'
CREATE_NETWORK_SCRIPT = ANSIBLE_FOLDER_PATH+"create_l3net.yaml"
CREATE_BRNS_CONN_SCRIPT = ANSIBLE_FOLDER_PATH+"create_brns_conn.yaml"
CREATE_VM_SCRIPT = ANSIBLE_FOLDER_PATH+"create_vm.yaml"
DELETE_NETWORK_SCRIPT = ANSIBLE_FOLDER_PATH+"delete_l3net.yaml"
DELETE_BRNS_CONN_SCRIPT = ANSIBLE_FOLDER_PATH+"delete_brns_conn.yaml"
DELETE_VM_SCRIPT = ANSIBLE_FOLDER_PATH+"delete_vm.yaml"
RUN_DHCLIENT_SCRIPT = ANSIBLE_FOLDER_PATH+"run_dhclient.yaml"

def read_yaml_data(f_name):
  data = None
  with open(f_name) as stream:
    data = yaml.safe_load(stream)
  return data

def write_yaml_data(data, f_name):
  with open(f_name, 'w') as outfile:
    yaml.dump(data, outfile)

def createFunc(yFile, logFile):
    if yFile['controllerNet'].lower()=="y":

        #vm = hypervisor, template, vm_name - create_vm.yaml, controllerTemplate.xml.j2, mem, vcpu, net
        #start_ip, bridge_name, start_ip, end_ip, network_name
        #bridge = hyp, bridge_name,  namespace(tenantNAme_transit), veth1, veth2

        print("Creating  ControllerNet ")

        # variables
        networkName = str(yFile["tenantID"])+"controller_net"
        bridgeName = str(yFile["tenantID"])+"controller_br"
        br_ip = str(yFile['tenantID'])+'.0.0.1'
        start_ip = str(yFile['tenantID'])+'.0.0.2'
        end_ip = str(yFile['tenantID'])+'.0.0.254'

        # create controller network
        command = "sudo ansible-playbook " + CREATE_NETWORK_SCRIPT + " -e hypervisor=" + yFile['hypervisorType'] + " -e br_ip=" +br_ip+" -e start_ip="+start_ip+" -e end_ip="+end_ip+" -e network_name="+networkName+" -e bridge_name="+bridgeName
        subprocess.call([command],shell=True)
        logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Creating  Controller  : " + command + "\n")

        print("Creating Bridge to namespace connection ")

        # create controller to transit ns connection
        comand = "sudo ansible-playbook " + CREATE_BRNS_CONN_SCRIPT + " -e hypervisor=" + yFile['hypervisorType'] + " -e veth1=" +str(yFile["tenantID"])+"_1"+" -e veth2="+str(yFile["tenantID"])+"_2"+" -e namespace="+str(yFile['tenantName'])+"_transit"+" -e bridge_name="+bridgeName
        subprocess.call([command],shell=True)
        
        # run dhclient on the namespace
        command = "sudo ansible-playbook " + RUN_DHCLIENT_SCRIPT + " -e hypervisor=" + yFile['hypervisorType'] + " -e namespace=" + str(yFile['tenantName'] + "_transit -e veth=" + str(yFile["tenantID"])+"_2"
        
        subprocess.call([command],shell=True)

        logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Creating  Bridge to namespace connection  : " + command + "\n")

    if "vms" in yFile:
        for vm in yFile["vms"]:
            print("Creating  VM : "+str(vm['vmName']))

            # create controller vm
            command = "sudo ansible-playbook " + CREATE_VM_SCRIPT + " -e hypervisor=" + yFile['hypervisorType'] +" -e vm_name="+str(vm['vmName']) +" -e mem="+str(vm['mem'])+" -e vcpu="+str(vm['vcpu']) +" -e network="+networkName
            subprocess.call([command],shell=True)
            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Creating Controller VM : " + command  + "\n")

def deleteFunc(yFile, logFile):
    #for net  - hypervisor, net_name, bridge_name
    #for vm - hypervsr, vm_name
    #for bridge - hyp, veth1
    networkName = str(yFile["tenantID"])+"controller_net"
    bridgeName = str(yFile["tenantID"])+"controller_br"
    if "vms" in yFile:
        for vm in yFile["vms"]:
            print("Deleting  VM "+str(vm["vmName"]))

            command = "sudo ansible-playbook " + DELETE_VM_SCRIPT + " -e hypervisor=" + yFile['hypervisorType']+" -e vm_name="+str(vm["vmName"])+" -e network="+networkName
            subprocess.call([command],shell=True)
            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Deleting Controller : " + command + "\n")

    if yFile['controllerNet'].lower()=="y":
        print("Deleting  Controller ")
        command = "sudo ansible-playbook " + DELETE_NETWORK_SCRIPT + " -e hypervisor=" + yFile['hypervisorType'] + " -e network_name="+networkName+ " -e bridge_name="+bridgeName
        subprocess.call([command],shell=True)
        logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Deleting ControllerNet : " + command + "\n")

        print("Deleting Bridge ")
        command = "sudo ansible-playbook " + DELETE_BRNS_CONN_SCRIPT + " -e hypervisor=" + yFile['hypervisorType'] + " -e veth1=" +str(yFile["tenantID"])+"_1"
        subprocess.call([command],shell=True)
        logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Creating  Bridge  : " + command + "\n")


def checkYAML(yFile, logFile):
    if not "tenantInfo" in yFile:
        logging.error("\nERROR: Cannot perform create operation!!!")
        logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Tenant Id missing in yaml file : "+ str(sys.argv)+"\n")
        exit(0)
    if not ("vms" in yFile['tenantInfo'] or "controllerNet" in yFile['tenantInfo']):
        logging.error("\nERROR: Cannot perform create operation!!!")
        logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Wrong config in yaml file : "+ str(sys.argv)+"\n")
        exit(0)

def main():

  fileName = "/var/log/log_"+time.strftime("%Y%m%d")+".txt"
  logFile = open(fileName, 'a+')

  if(len(sys.argv)<2):
        logging.error("\nERROR: less than 2 arguments given!!! Require 2 arguments to run")
        logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Argument Length Error: "+ str(sys.argv)+"\n")
        exit(0)
  else:
        yFileName = sys.argv[2]
    # check if yaml file is passed
        if yFileName.endswith(".yml") or yFileName.endswith(".yaml"):
            try:
                #open the yaml file
                yFile = read_yaml_data(yFileName)
                checkYAML(yFile, logFile)
                # check for the 1st argument i.e., create or delete
                if str(sys.argv[1]).lower()=="delete":
                    print("\nPerforming delete operation depending upon the file")
                    deleteFunc(yFile["tenantInfo"], logFile)
                    
                elif str(sys.argv[1]).lower()=="create":
                    logging.info("\nPerforming create operation depending upon the file")
                    createFunc(yFile["tenantInfo"], logFile)
                else:
                    logging.error("\nERROR: Unrecognized Command!!!")
                    logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Wrong Command : "+ str(sys.argv)+"\n")
                    exit(0)
            except Exception as ex:
                logging.error(str(ex))
                exit(0)
        else:
            logging.error("\nERROR: No yaml/yml file found!!!")
            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   No yaml/yml file found : "+ str(sys.argv)+"\n")
            exit(0)
  logFile.close()



if __name__ == '__main__':
    main()

