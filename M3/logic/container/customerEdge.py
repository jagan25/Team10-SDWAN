import sys
import yaml
import logging
import subprocess
import time

CONFIG_FOLDER_PATH = '/etc/config/container/'
ANSIBLE_FOLDER_PATH = '/var/scripts/container/'
CREATE_NETWORK_SCRIPT = ANSIBLE_FOLDER_PATH+"create_l2net.yaml"
CREATE_BRNS_CONN_SCRIPT = ANSIBLE_FOLDER_PATH+"create_brns_conn.yaml"
CREATE_CONTAINER_SCRIPT = ANSIBLE_FOLDER_PATH+"create_container.yaml"
CREATE_DOC_CONN_SCRIPT = ANSIBLE_FOLDER_PATH+"create_doc_conn.yaml"
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

def createCE(yFile, yFileName, logFile):
    print("creating ce")
    print(yFile)
    if "container" in yFile:
        print(" Creating CE network")

        # variables
        transit = yFile['tenant_name']+yFile['site']
        controller_net = str(yFile['tenant_id'])+'controller_net'

        for cont in yFile["container"]:
            #variables
            bridge_name = transit+'CE_net'
            controller_br = yFile["tenant_name"]+'cont_br'
            
            print("Creating Customer Edge container : CE"+str(cont['id']))

            # create customer edge container
            command = "sudo ansible-playbook " + CREATE_CONTAINER_SCRIPT + " -e hypervisor=" + yFile['hypervisorType'] +" -e container="+transit+"CE"+ str(cont['id']) + " -e image="+str(cont['image'])
            subprocess.call([command],shell=True)
            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Creating Customer Edge Container : " + command  + "\n")

            # create connection to controller br
            print("Connecting the container to controller bridge")
            veth1 = transit+"CE"+ str(cont['id']) + 'cbr1'
            veth2 = transit+"CE"+ str(cont['id']) + 'cbr2'
            command = "sudo ansible-playbook " + CREATE_DOC_CONN_SCRIPT + " -e hypervisor=" + yFile['hypervisorType'] + " -e option=none -e option2=none -e veth1=" +veth1+ " -e veth2="+veth2+" -e bridge_name="+ controller_br + " -e container=" + transit+"CE"+ str(cont['id']) + " -e option=run_dhclient"

            subprocess.call([command],shell=True)
            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Connecting to Controller network : " + command  + "\n")

            # attach customer edge to Site-Bridge Network
            print("Connecting CE to CE network")
            veth1 = transit+'CE'+str(cont['id'])+'1'
            veth2 = transit+'CE'+str(cont['id'])+'2'
            ns_name = yFile['tenant_name']+yFile['site']
            command = "sudo ansible-playbook " + CREATE_DOC_CONN_SCRIPT + " -e hypervisor=" + yFile['hypervisorType'] + " -e veth1=" +veth1+ " -e veth2="+veth2+" -e bridge_name="+bridge_name + " -e container=" +transit+"CE"+ str(cont['id'])+ " -e option=assign_ip  -e option2=assign_default -e ns_name="+ ns_name +" -e ip="+str(yFile['tenant_id'])+"."+str(yFile['site_id'])+".0."+str(cont['id'])+"/24"
            subprocess.call([command],shell=True)
            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Connecting to Site-Bridge network : " + command  + "\n")

            # create connection to PE network
            for p in cont['PE']:
                print("Connecting CE to PE network")
                veth1 = transit+'CE'+str(cont['id'])+'PE'+str(p)+'1'
                veth2 = transit+'CE'+str(cont['id'])+'PE'+str(p)+'2'
                bridge = transit+'PE'+str(p)
                command = "sudo ansible-playbook "+ CREATE_DOC_CONN_SCRIPT + " -e hypervisor="+ yFile['hypervisorType'] + " -e option=none -e option2=none -e veth1="+veth1+" -e veth2="+veth2+" -e bridge_name="+bridge+" -e container="+transit+"CE"+ str(cont['id'])+" -e option=assign_ip -e ip="+str(yFile['tenant_id'])+"."+str(yFile['site_id'])+"."+str(p)+"."+str(cont['id'])+"/24"
                subprocess.call([command],shell=True)
                logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Connecting CE to PE network : " + command  + "\n")

def deleteCE(yFile, logFile):
    
    if yFile['delete_container']=='y':
        for cont in yFile['container']:
            # delete CE Container
            transit = yFile['tenant_name']+yFile['site']
            print("deleting container")
            command = "sudo ansible-playbook " + DELETE_CONTAINER_SCRIPT + " -e hypervisor=" + yFile['hypervisorType']+" -e container="+transit+"CE"+ str(cont['id'])
            subprocess.call([command],shell=True)
            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Deleting CE : " + command + "\n")
            print("Deleting link between CE and CE network")
            veth = transit+'CE'+str(cont['id'])+'1'
            command = 'sudo ansible-playbook ' + DELETE_BRNS_CONN_SCRIPT + ' -e hypervisor='+yFile['hypervisorType']+' -e veth1='+veth
            subprocess.call([command],shell=True)
            for p in cont['PE']:
                print("Deleting link between CE and PE")
                veth = transit+'CE'+str(cont['id'])+'PE'+str(p)+'1'
                command = 'sudo ansible-playbook ' + DELETE_BRNS_CONN_SCRIPT + ' -e hypervisor='+yFile['hypervisorType']+" -e veth1="+veth
                subprocess.call([command],shell=True)

    else:
        for c in yFile['container']:
            if c['delete_link']=='y':
                for p in c['PE']:
                    print("Deleting link between CE and PE")
                    veth = transit+'CE'+str(c['id'])+'PE'+str(p)+'1'
                    command = 'sudo ansible-playbook ' + DELETE_BRNS_CONN_SCRIPT + ' -e hypervisor='+yFile['hypervisorType']+" -e veth1="+veth
                    subprocess.call([command],shell=True)

        
def checkYaml(yFile, logFile):
    if 'CE' not in yFile:
        print("ERROR!!! Missing 'CE' key in YAML file")
        logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   ERROR!!! Missing 'CE' key in YAML file : "+ str(sys.argv) +"\n")
        exit(0)
    if not 'container' in yFile['CE']:
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
                yFile = read_yaml_data(CONFIG_FOLDER_PATH +  yFileName)
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

