import sys
import yaml
import logging
import subprocess
import time

CONFIG_FOLDER_PATH = '/etc/config/'
ANSIBLE_FOLDER_PATH = '/var/scripts/'
CREATE_NETWORK_SCRIPT = ANSIBLE_FOLDER_PATH+"create_l2net.yaml"
CREATE_BRNS_CONN_SCRIPT = ANSIBLE_FOLDER_PATH+"create_brns_conn.yaml"
CREATE_VM_SCRIPT = ANSIBLE_FOLDER_PATH+"create_vm.yaml"
DELETE_NETWORK_SCRIPT = ANSIBLE_FOLDER_PATH+"delete_l2net.yaml"
DELETE_BRNS_CONN_SCRIPT = ANSIBLE_FOLDER_PATH+"delete_brns_conn.yaml"
DELETE_VM_SCRIPT = ANSIBLE_FOLDER_PATH+"delete_vm.yaml"

def read_yaml_data(f_name):
  data = None
  with open(f_name) as stream:
    data = yaml.safe_load(stream)
  return data

def write_yaml_data(data, f_name):
  with open(f_name, 'w') as outfile:
    yaml.dump(data, outfile)

def createPE(yFile, yFileName, logFile):
    print("creating pe")
    print(yFile)
    if "IPrange" in yFile:
        print(" Creating PE network")
        # log
        logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Creating IP Ranges for PE : "+ str(yFile["tenant_name"])+"\n")

        # variables
        bridge_name = yFile['tenant_name']+'_PT_br'
        network_name = yFile['tenant_name']+'_PT_net'
        veth1 =  yFile['tenant_name']+'PT1'
        veth2 =  yFile['tenant_name']+'PT2'
        transit = yFile['tenant_name']+'_transit'

        # create l2 bridge
        command = "sudo ansible-playbook " + CREATE_NETWORK_SCRIPT + " -e hypervisor="+yFile['hypervisorType']+" -e bridge_name="+bridge_name+" -e network_name="+network_name
        subprocess.call([command], shell = True)
        logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Creating L2 Bridge : " + command + "\n")

        # connect bridge with transit namespace
        command = "sudo ansible-playbook " + CREATE_BRNS_CONN_SCRIPT + " -e hypervisor="+yFile['hypervisorType']+" -e veth1="+veth1+" -e veth2="+veth2+" -e bridge_name="+bridge_name+" -e namespace="+transit
        subprocess.call([command], shell=True)
        logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Creating  Bridge to namespace connection  : " + command + "\n")


    if "vms" in yFile:
        print("test")
        network_name = yFile['tenant_name']+'_PT_net'
        controller_net = str(yFile['tenant_id'])+'controller_net'
        for vm in yFile["vms"]:
            print("Creating  VM : "+str(vm['PE_name']))

            # create provider vm
            command = "sudo ansible-playbook " + CREATE_VM_SCRIPT + " -e hypervisor=" + yFile['hypervisorType'] +" -e vm_name="+str(yFile['tenant_name'])+str(vm['PE_name']) +" -e mem="+str(vm['mem'])+" -e vcpu="+str(vm['vcpu']) +" -e network="+ controller_net +" -vvv"
            subprocess.call([command],shell=True)
            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Creating Provider Edge VM : " + command  + "\n")

            # attach provider edge to PE-Transit Network
            command = "sudo virsh attach-interface --domain " + str(vm['PE_name']) + " --type network " + network_name  + " --model virtio --config --live"
            subprocess.call([command], shell=True)
            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Attaching Provider Edge to PE-Transit Network : " + command + "\n")

def deletePE(yFile, logFile):
    if 'vms' in yFile:
        for vm in yFile['vms']:
            # delete PE VM
            command = "sudo ansible-playbook " + DELETE_VM_SCRIPT + " -e hypervisor=" + yFile['hypervisorType']+" -e vm_name=" + str(vm["PE_name"])
            subprocess.call([command], shell=True)
            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Deleting PE : " + command + "\n")

    if 'IPrange' in yFile:
        network_name = yFile['tenant_name']+'_PT_net'
        bridge_name = yFile['tenant_name']+'_PT_br'
        veth1 =  yFile['tenant_name']+'PT1'

        # delete l2 network
        command = "sudo ansible-playbook " + DELETE_NETWORK_SCRIPT + " -e hypervisor=" + yFile['hypervisorType']+" -e network_name="+ network_name +" -e bridge_name="+ bridge_name
        subprocess.call([command], shell=True)
        logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Deleting PE-Transit network : " + command + "\n")

        # delete veth pair
        command = "sudo ansible-playbook " + DELETE_BRNS_CONN_SCRIPT + " -e hypervisor=" + yFile['hypervisorType']+" -e veth1="+ veth1
        subprocess.call([command], shell=True)
        logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Deleting PE-Transit connection : " + command + "\n")

def checkYaml(yFile, logFile):
    if 'PE' not in yFile:
        print("ERROR!!! Missing 'PE' key in YAML file")
        logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   ERROR!!! Missing 'PE' key in YAML file : "+ str(sys.argv) +"\n")
        exit(0)
    if not 'IPrange' in yFile['PE'] and not 'vms' in yFile['PE']:
        print("ERROR!!! Cannot process the given YAML file. MISSING KEYS!!!")
        logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   ERROR!!! Cannot process the given YAML file. MISSING KEYS!!! : "+ str(sys.argv) +"\n")
        exit(0)

def main():

    fileName = "/var/log/log_"+time.strftime("%Y%m%d")+".txt"
    logFile = open(fileName, 'a+')

    if(len(sys.argv)<2):
        logging.error("ERROR: No arguments given")
        logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   No Arguments Error: "+ str(sys.argv)+"\n")
        exit(0)

    else:
        yFileName = sys.argv[2]
        # print(yFileName)
        # check if yaml file is passed
        if yFileName.endswith(".yml") or yFileName.endswith(".yaml"):
            try:
                # open the yaml file
                yFile = read_yaml_data(yFileName)
                #print(yFile)
                checkYaml(yFile, logFile)
                print("test")
                # check for the 1st argument i.e., create or delete
                if str(sys.argv[1]).lower() == "delete":
                    print("Performing delete operation depending upon the file")
                    deletePE(yFile['PE'], logFile)
                elif str(sys.argv[1]).lower() == "create":
                    print("Performing create operation depending upon the file")
                    createPE(yFile['PE'], yFileName, logFile)
            except:
                print("ERROR!!!")
                logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Error In Executing Command : "+ str(sys.argv) +"\n")
        else:
            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Error In Executing Command : "+ str(sys.argv) +"\n")
            
    logFile.close()

if __name__ == '__main__':
    main()

