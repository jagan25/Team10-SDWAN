import sys
import yaml
import logging
import subprocess
import time

CONFIG_FOLDER_PATH = '/etc/config/'
ANSIBLE_FOLDER_PATH = '/var/scripts/'
CREATE_NETWORK_SCRIPT = ANSIBLE_FOLDER_PATH+"create_l2net.yaml"
CREATE_CONN = ANSIBLE_FOLDER_PATH+"create_conn.yaml"
DELETE_NETWORK_SCRIPT = ANSIBLE_FOLDER_PATH+"delete_l2net.yaml"

def read_yaml_data(f_name):
  data = None
  with open(f_name) as stream:
    data = yaml.safe_load(stream)
  return data

def write_yaml_data(data, f_name):
  with open(f_name, 'w') as outfile:
    yaml.dump(data, outfile)

def createCEPECONN(yFile, yFileName, logFile):
    print("creating cepe connection")
    print(yFile)
    if "PEs" in yFile:
        print(" Creating CEPE connection")

        for pe in yFile["PEs"]:
            #variables
            bridge_name = yFile['tenant_name']+yFile['CE_name']+pe+'_br'
            network_name = yFile['tenant_name']+yFile['CE_name']+pe+'_net'
            
            # create l2 bridge
            command = "sudo ansible-playbook " + CREATE_NETWORK_SCRIPT + " -e hypervisor="+yFile['hypervisorType']+" -e bridge_name="+bridge_name+" -e network_name="+network_name
            subprocess.call([command], shell = True)
            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Creating L2 Bridge : " + command + "\n")

            #Create CE connection
            command = "sudo ansible-playbook "+ CREATE_CONN + " -e vm="+yFile['CE_name']+" -e network="+network_name+ " -e hypervisor="+yFile['hypervisorType']
            subprocess.call([command], shell = True)
            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Creating CE connection : " + command + "\n")

            #Create PE connection
            command = "sudo ansible-playbook "+ CREATE_CONN + " -e vm="+pe+" -e network="+network_name+ " -e hypervisor="+yFile['hypervisorType']
            subprocess.call([command], shell = True)
            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Creating CE connection : " + command + "\n")

def deleteCEPECONN(yFile, logFile):
    if 'PEs' in yFile:
        for pe in yFile['PEs']:
            #variables
            bridge_name = yFile['tenant_name']+yFile['CE_name']+pe+'_br'
            network_name = yFile['tenant_name']+yFile['CE_name']+pe+'_net'
            
            # delete l2 bridge
            command = "sudo ansible-playbook " + DELETE_NETWORK_SCRIPT + " -e hypervisor="+yFile['hypervisorType']+" -e bridge_name="+bridge_name+" -e network_name="+network_name
            subprocess.call([command], shell = True)
            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Deleting L2 Bridge : " + command + "\n")
            
def checkYaml(yFile, logFile):
    if 'CEPE' not in yFile:
        print("ERROR!!! Missing 'CEPE' key in YAML file")
        logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   ERROR!!! Missing 'CE' key in YAML file : "+ str(sys.argv) +"\n")
        exit(0)
    if not 'PEs' in yFile['CEPE']:
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
                    deleteCEPECONN(yFile['CEPE'], logFile)
                elif str(sys.argv[1]).lower() == "create":
                    print("Performing create operation depending upon the file")
                    createCEPECONN(yFile['CEPE'], yFileName, logFile)
            except:
                print("ERROR!!!")
                logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Error In Executing Command : "+ str(sys.argv) +"\n")
        else:
            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Error In Executing Command : "+ str(sys.argv) +"\n")
            
    logFile.close()

if __name__ == '__main__':
    main()

