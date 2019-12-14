import sys
import yaml
import logging
import subprocess
import time
import re
import json

CONFIG_FOLDER_PATH = '/etc/config/container/'
ANSIBLE_FOLDER_PATH = '/var/scripts/container/'
CREATE_NETWORK_SCRIPT = ANSIBLE_FOLDER_PATH+"create_l2net.yaml"
CREATE_BRNS_CONN_SCRIPT = ANSIBLE_FOLDER_PATH+"create_brns_conn.yaml"
CREATE_DOC_CONN_SCRIPT = ANSIBLE_FOLDER_PATH+"create_doc_conn.yaml"
CREATE_CONTAINER_SCRIPT = ANSIBLE_FOLDER_PATH+"create_container.yaml"
DELETE_NETWORK_SCRIPT = ANSIBLE_FOLDER_PATH+"delete_l2net.yaml"
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

def createPE(yFile, logFile):
    print("creating pe")
    print(yFile)
    if yFile['change_net'].lower()=='y':
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
        command = "sudo ansible-playbook " + CREATE_NETWORK_SCRIPT + " -e hypervisor="+yFile['hypervisorType']+" -e option=none -e bridge_name="+bridge_name+" -e network_name="+network_name
        subprocess.call([command], shell = True)
        logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Creating L2 Bridge : " + command + "\n")

        # connect bridge with transit namespace
        if yFile['hypervisorType'] == 'primary':
            o_ip = str(yFile['tenant_id'])+".0.2.254/24"
        else:
            o_ip = str(yFile['tenant_id'])+".255.2.254/24"
        command = "sudo ansible-playbook " + CREATE_BRNS_CONN_SCRIPT + " -e hypervisor="+yFile['hypervisorType']+" -e veth1="+veth1+" -e veth2="+veth2+" -e bridge_name="+bridge_name+" -e namespace="+transit +" -e option=assign_ip -e ip="+o_ip
        subprocess.call([command], shell=True)
        logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Creating  Bridge to namespace connection  : " + command + "\n")

        # assign ip address
        #command = "sudo ip netns exec "+transit +" ip add a "+ str(yFile['tenant_id'])+".0.2.254/24 dev "+veth2 



        #print(command)
        #subprocess.call([command], shell=True)
        #logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Assigning IP to transit to PE connection  : " + command + "\n")

    if "containers" in yFile:
        controller_br = str(yFile['tenant_name'])+'cont_br'
        bridge_name = yFile['tenant_name']+'_PT_br'
        for c in yFile["containers"]:
            print("Creating  VM : "+str(c['PE_name']))
            # create provider vm
            container = str(yFile['tenant_name'])+str(c['PE_name'])
            #print(container)
            command = "sudo ANSIBLE_STDOUT_CALLBACK=oneline ansible-playbook " + CREATE_CONTAINER_SCRIPT + " -e hypervisor=" + yFile['hypervisorType'] +" -e container="+ container + " -e image=" + c['image'] + " -e tid="+str(yFile['tenant_id'])
            #print(command)
            check_output = subprocess.check_output([command],shell=True)
            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Creating Provider Edge Container : " + command  + "\n")
            
            # connect to controller network
            print("Connecting the container to controller bridge")
            veth1 = container + 'cbr1'
            veth2 = container + 'cbr2'
            command = "sudo  ANSIBLE_STDOUT_CALLBACK=oneline ansible-playbook " + CREATE_DOC_CONN_SCRIPT + " -e hypervisor=" + yFile['hypervisorType'] + " -e veth1=" +veth1+ " -e veth2="+veth2+" -e bridge_name="+ controller_br + " -e container=" + str(container) + " -e option=run_dhclient -e option2=none -e tid="+str(yFile['tenant_id'])
            

            check_output = subprocess.check_output([command],shell=True)
            print(check_output)
            r1 = re.search(r"(([0-2]?[0-9]?[0-9]\.)([0]\.)([1]\.)([0-2]?[0-9]?[0-9]))",str(check_output))
            print(r1)
            with open('/etc/config/container/aliveStatus.txt',"r+") as f:
                fileData = json.load(f)
                pe = {}
                print(r1.group(0))
                pe['ip'] = r1.group(0)
                pe['name'] = container
                pe['1astPing'] = time.time()
                fileData['status'].append(pe)
                f.seek(0)
                f.truncate()
                json.dump(fileData, f)
                print(fileData)
            f.close()

            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Connecting to Controller network : " + command  + "\n")

            with open('/etc/config/container/PEConfig.txt',"r+") as f:
                fileData = json.load(f)
                pe = {}
                pe[container]={}
                pe[container]['ip'] = r1.group(0)
                fileData['ProviderEdges'].append(pe)
                f.seek(0)
                f.truncate()
                json.dump(fileData, f)
            f.close()

            with open('/etc/ansible/hosts','a+') as f:
                f.write(r1.group(0) + "  ansible_user=root ansible_ssh_private_key_file=/root/.ssh/id_rsa")
            f.close()


            # attach provider edge to PE-Transit Network
            if yFile['hypervisorType'] == 'primary':
                c_ip = str(yFile['tenant_id'])+'.0.2.'+str(c['id'])+"/24"
                default_ip = str(yFile['tenant_id'])+'.0.2.254'
            else:
                c_ip = str(yFile['tenant_id'])+'.255.2.'+str(c['id'])+"/24"
                default_ip = str(yFile['tenant_id'])+'.255.2.254'
            veth1 = 'veth_t'+str(yFile['tenant_id'])+'_p'+str(c['id'])+'_1'
            veth2 = 'veth_t'+str(yFile['tenant_id'])+'_p'+str(c['id'])+'_2'
            command = "sudo ansible-playbook " + CREATE_DOC_CONN_SCRIPT + " -e hypervisor=" + yFile['hypervisorType'] +" -e container="+ container + " -e bridge_name=" + bridge_name + " -e veth1=" + veth1 + " -e veth2=" + veth2+" -e option=assign_ip -e option2=default -e ip="+ c_ip +" -e default_ip="+default_ip
            #print(command)
            subprocess.call([command], shell=True)
            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Attaching Provider Edge Container to PE-transit Bridge : " + command  + "\n")

            with open('/etc/config/container/TPE_config.txt', "r+") as f:
                fileData = json.load(f)
                fileData['TransitEdges'][container] = c_ip[:-3]
                f.seek(0)
                f.truncate()
                json.dump(fileData, f)
            f.close()


def deletePE(yFile, logFile):
    if 'containers' in yFile:
        for c in yFile['containers']:
            container = str(yFile['tenant_name'])+str(c['PE_name'])
            # delete PE Container
            command = "sudo ansible-playbook " + DELETE_CONTAINER_SCRIPT + " -e hypervisor=" + yFile['hypervisorType']+" -e container=" + container
            subprocess.call([command], shell=True)
            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Deleting PE : " + command + "\n")

    if yFile['change_net'].lower()=='y':
        network_name = yFile['tenant_name']+'_PT_net'
        bridge_name = yFile['tenant_name']+'_PT_br'
        veth1 =  yFile['tenant_name']+'PT1'

        # delete l2 network
        command = "sudo ansible-playbook " + DELETE_NETWORK_SCRIPT + " -e hypervisor=" + yFile['hypervisorType']+" -e option=none -e network_name="+ network_name +" -e bridge_name="+ bridge_name
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
    if not 'change_net' in yFile['PE'] and not 'containers' in yFile['PE']:
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
                yFilePath = CONFIG_FOLDER_PATH + yFileName
                yFile = read_yaml_data(yFilePath)
                checkYaml(yFile, logFile)
                print("test")
                # check for the 1st argument i.e., create or delete
                if str(sys.argv[1]).lower() == "delete":
                    print("Performing delete operation depending upon the file")
                    deletePE(yFile['PE'], logFile)
                elif str(sys.argv[1]).lower() == "create":
                    print("Performing create operation depending upon the file")
                    createPE(yFile['PE'], logFile)
            except:
                print("ERROR!!!")
                logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Error In Executing Command : "+ str(sys.argv) +"\n")
        else:
            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Error In Executing Command : "+ str(sys.argv) +"\n")
            
    logFile.close()

if __name__ == '__main__':
    main()

