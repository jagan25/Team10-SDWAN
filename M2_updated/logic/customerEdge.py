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
CREATE_CONN = ANSIBLE_FOLDER_PATH+"create_conn.yaml"
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

def createCE(yFile, yFileName, logFile):
    print("creating ce")
    print(yFile)
    if "vms" in yFile:
        print(" Creating CE network")

        # variables
        transit = yFile['tenant_name']+yFile['site']
        controller_net = str(yFile['tenant_id'])+'controller_net'

        for vm in yFile["vms"]:
            #variables
            bridge_name = transit+vm['CE_name']
            network_name = transit+vm['CE_name']
            veth1 = transit+vm['CE_name']+'1'
            veth2 = transit+vm['CE_name']+'2'
            
            # create l2 bridge
            command = "sudo ansible-playbook " + CREATE_NETWORK_SCRIPT + " -e hypervisor="+yFile['hypervisorType']+" -e bridge_name="+bridge_name+" -e network_name="+network_name
            subprocess.call([command], shell = True)
            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Creating L2 Bridge : " + command + "\n")
            
            # connect bridge with transit namespace
            command = "sudo ansible-playbook " + CREATE_BRNS_CONN_SCRIPT + " -e hypervisor="+yFile['hypervisorType']+" -e veth1="+veth1+" -e veth2="+veth2+" -e bridge_name="+bridge_name+" -e namespace="+transit
            subprocess.call([command], shell=True)
            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Creating  Bridge to namespace connection  : " + command + "\n")
            
            print("Creating Customer Edge VM : "+str(vm['CE_name']))

            # create customer edge vm
            command = "sudo ansible-playbook " + CREATE_VM_SCRIPT + " -e hypervisor=" + yFile['hypervisorType'] +" -e vm_name="+str(vm['CE_name']) +" -e mem="+str(vm['mem'])+" -e vcpu="+str(vm['vcpu']) +" -e network="+ controller_net +" -vvv"
            subprocess.call([command],shell=True)
            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Creating Customer Edge VM : " + command  + "\n")

            # attach customer edge to Site-Bridge Network
            command = "sudo ansible-playbook "+ CREATE_CONN + " -e vm="+vm['CE_name']+" -e network="+network_name+ " -e hypervisor="+yFile['hypervisorType']
            subprocess.call([command], shell = True)
            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Attaching Customer Edge to CE-Site Network : " + command + "\n")

def deleteCE(yFile, logFile):
    if 'vms' in yFile:
        for vm in yFile['vms']:
            bridge_name = yFile['tenant_name']+vm['CE_name']+'_br'
            network_name = yFile['tenant_name']+vm['CE_name']+'_net'
            veth1 =  yFile['tenant_name']+vm['CE_name']+'1'
            
            # delete CE VM
            command = "sudo ansible-playbook " + DELETE_VM_SCRIPT + " -e hypervisor=" + yFile['hypervisorType']+" -e vm_name=" + str(vm["CE_name"])
            subprocess.call([command], shell=True)
            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Deleting CE : " + command + "\n")
            
            # delete l2 network
            command = "sudo ansible-playbook " + DELETE_NETWORK_SCRIPT + " -e hypervisor=" + yFile['hypervisorType']+" -e network_name="+ network_name +" -e bridge_name="+ bridge_name
            subprocess.call([command], shell=True)
            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Deleting CE-Site network : " + command + "\n")
            
            # delete veth pair
            command = "sudo ansible-playbook " + DELETE_BRNS_CONN_SCRIPT + " -e hypervisor=" + yFile['hypervisorType']+" -e veth1="+ veth1
            subprocess.call([command], shell=True)
            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Deleting CE-Site connection : " + command + "\n")

def checkYaml(yFile, logFile):
    if 'CE' not in yFile:
        print("ERROR!!! Missing 'CE' key in YAML file")
        logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   ERROR!!! Missing 'CE' key in YAML file : "+ str(sys.argv) +"\n")
        exit(0)
    if not 'vms' in yFile['CE']:
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
                    deleteCE(yFile['CE'], logFile)
                elif str(sys.argv[1]).lower() == "create":
                    print("Performing create operation depending upon the file")
                    createCE(yFile['CE'], yFileName, logFile)
            except:
                print("ERROR!!!")
                logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Error In Executing Command : "+ str(sys.argv) +"\n")
        else:
            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Error In Executing Command : "+ str(sys.argv) +"\n")
            
    logFile.close()

if __name__ == '__main__':
    main()

