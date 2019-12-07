import sys
import yaml
import logging
import subprocess
import time

CONFIG_FOLDER_PATH = '/etc/config/container/'
ANSIBLE_FOLDER_PATH = '/var/scripts/container/'
CREATE_NETWORK_SCRIPT = ANSIBLE_FOLDER_PATH+"create_l3net.yaml"
CREATE_NETWORK_SCRIPT2 = ANSIBLE_FOLDER_PATH+"create_l2net.yaml"
CREATE_BRNS_CONN_SCRIPT = ANSIBLE_FOLDER_PATH+"create_brns_conn.yaml"
CREATE_CONTAINER_SCRIPT = ANSIBLE_FOLDER_PATH+"create_container.yaml"
CREATE_DOC_CONN_SCRIPT = ANSIBLE_FOLDER_PATH+"create_doc_conn.yaml"
DELETE_NETWORK_SCRIPT = ANSIBLE_FOLDER_PATH+"delete_l3net.yaml"
DELETE_NETWORK_SCRIPT2 = ANSIBLE_FOLDER_PATH+"delete_l2net.yaml"
DELETE_BRNS_CONN_SCRIPT = ANSIBLE_FOLDER_PATH+"delete_brns_conn.yaml"
DELETE_CONTAINER_SCRIPT = ANSIBLE_FOLDER_PATH+"delete_container.yaml"
DELETE_DOC_CONN_SCRIPT = ANSIBLE_FOLDER_PATH+"delete_doc_conn.yaml"
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
    bridgeName = str(yFile["tenantName"])+"cont_br"
    if yFile['controllerNet'].lower()=="y":
        print("Creating  ControllerNet ")

        # variables
        networkName = str(yFile["tenantName"])+"cont_net"
        br_ip = str(yFile['tenantID'])+'.0.1.1'
        start_ip = str(yFile['tenantID'])+'.0.1.2'
        end_ip = str(yFile['tenantID'])+'.0.1.254'

        # create controller network
        if yFile['hypervisorType']=="primary":
            command = "sudo ansible-playbook " + CREATE_NETWORK_SCRIPT + " -e hypervisor=" + yFile['hypervisorType'] + " -e br_ip=" +br_ip+" -e start_ip="+start_ip+" -e end_ip="+end_ip+" -e network_name="+networkName+" -e bridge_name="+bridgeName+" -e option=create_vxlan -e id="+ str(yFile['tenantID'])+" -e vxlan_name="+str(yFile['tenantName'])+" -e remoteIP="+yFile['remoteIP']
            subprocess.call([command],shell=True)
            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Creating  Controller in the primary hupervisor : " + command + "\n")

        elif yFile['hypervisorType']=="secondary":
            command = "sudo ansible-playbook " + CREATE_NETWORK_SCRIPT2 + " -e hypervisor=" + yFile['hypervisorType'] +" -e bridge_name="+ bridgeName +" -e network_name=" + networkName + " -e vxlan_name=" + str(yFile['tenantName']) +" -e id=" + str(yFile['tenantID']) + " -e remoteIP="+ yFile['remoteIP'] + " -e option=create_vxlan"
            subprocess.call([command],shell=True)
            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Creating  Controller in the secondary hypervisor : " + command + "\n")

        print("Creating Bridge to namespace connection ")

        # create controller to transit ns connection
        veth1 = str(yFile["tenantID"])+"_1"
        veth2 = str(yFile["tenantID"])+"_2"
        namespace = str(yFile['tenantName'])+"_transit"
        command = "sudo ansible-playbook " + CREATE_BRNS_CONN_SCRIPT + " -e hypervisor=" + yFile['hypervisorType'] + " -e veth1=" + veth1 +" -e veth2="+ veth2 +" -e namespace="+namespace+" -e bridge_name="+bridgeName+ " -e option=run_dhclient"
        subprocess.call([command],shell=True)

        #ommand = "sudo ip netns exec "+namespace+ " dhclient " +veth2
        #subprocess.call([command],shell=True
        
    if "containers" in yFile:
        for c in yFile["containers"]:
            print("Creating  Controller container : "+str(c['cName']))
            # create controller container
            container = str(c['cName'])
            command = "sudo ansible-playbook " + CREATE_CONTAINER_SCRIPT + " -e hypervisor=" + yFile['hypervisorType'] +" -e container="+ container + " -e image="+str(c['image'])
            subprocess.call([command],shell=True)
            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Creating Controller Container : " + command  + "\n")
            
            # connect to controller network
            print("Connecting the container to controller bridge")
            veth1 = 't' + str(yFile['tenantID']) + '_' + str(c['cID']) + 'cbr1'
            veth2 = 't' + str(yFile['tenantID']) + '_' + str(c['cID']) + 'cbr2'

            command = "sudo ansible-playbook " + CREATE_DOC_CONN_SCRIPT + " -e hypervisor=" + yFile['hypervisorType'] + " -e veth1=" +veth1+ " -e veth2="+veth2+" -e bridge_name="+bridgeName + " -e container=" + str(container) + " -e option=run_dhclient -e option2=none"

            subprocess.call([command],shell=True)
            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Connecting to Controller network : " + command  + "\n")

            #Run dhclient on container
            #command = "sudo ansible-playbook "+ RUN_DHCLIENT_SCRIPT + " -e hypervisor=" + yFile['hypervisorType'] + " -e container="+container
            #subprocess.call([command],shell=True)
            #logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Running dhclient on controller : " + command  + "\n")


def deleteFunc(yFile, logFile):
    #for net  - hypervisor, net_name, bridge_name
    #for vm - hypervsr, vm_name
    #for bridge - hyp, veth1
    networkName = str(yFile["tenantName"])+"cont_net"
    bridgeName = str(yFile["tenantName"])+"cont_br"
    if "containers" in yFile:
        for c in yFile["containers"]:
            veth = 't' + str(yFile['tenantID']) + '_' + str(c['cID']) + 'cbr2'
            print("Deleting  container "+str(c["cName"]))
            command = "sudo ansible-playbook " + DELETE_CONTAINER_SCRIPT + " -e hypervisor=" + yFile['hypervisorType']+" -e container="+str(c["cName"])+" -e veth="+veth
            subprocess.call([command],shell=True)
            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Deleting Controller at Primary: " + command + "\n")

    if yFile['controllerNet'].lower()=="y":
        if yFile['hypervisorType'] == 'primary':
            print("Deleting  Controller net at primary")
            command = "sudo ansible-playbook " + DELETE_NETWORK_SCRIPT + " -e hypervisor=" + yFile['hypervisorType'] + " -e network_name="+networkName+ " -e bridge_name="+bridgeName+" -e option=delete_vxlan -e vxlan_name="+yFile['tenantName']
            subprocess.call([command],shell=True)
            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Deleting ControllerNet at primary : " + command + "\n")

        elif yFile['hypervisorType'] == 'secondary':
            command = "sudo ansible-playbook "+ DELETE_NETWORK_SCRIPT2 + " -e hypervisor=" + yFile['hypervisorType'] + " -e bridge_name=" + bridgeName+ " -e network_name=" + networkName + " -e vxlan_name=" + yFile['tenantName'] + " -e option=delete_vxlan"
            subprocess.call([command],shell=True)
            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Deleting ControllerNet at secondary : " + command + "\n")

        print("Deleting Bridge to namespace connection")
        command = "sudo ansible-playbook " + DELETE_BRNS_CONN_SCRIPT + " -e hypervisor=" + yFile['hypervisorType'] + " -e veth1=" +str(yFile["tenantID"])+"_1"
        subprocess.call([command],shell=True)
        logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Deleting  Bridge  : " + command + "\n")




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
                yFile = read_yaml_data(CONFIG_FOLDER_PATH+yFileName)
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

