import sys
import yaml
import logging
import subprocess
import time

CONFIG_FOLDER_PATH = '/etc/config/'
ANSIBLE_FOLDER_PATH = '/var/scripts/'
CREATE_NS_SCRIPT = ANSIBLE_FOLDER_PATH+"create_ns.yaml"
DELETE_NS_SCRIPT = ANSIBLE_FOLDER_PATH+"delete_ns.yaml"

def read_yaml_data(f_name):
  data = None
  with open(f_name) as stream:
    data = yaml.safe_load(stream)
  return data

def write_yaml_data(data, f_name):
  with open(f_name, 'w') as outfile:
    yaml.dump(data, outfile)

def createTransit(config, logFile):
    print('Creating transit VPC')
    hypervisorIP = createIP(str(config['tenant']['tenant_id']), "1")
    transitIP = createIP(str(config['tenant']['tenant_id']), "2")
    transitNS = str(config['tenant']['tenant_name'])+'_transit'
    command = "sudo ansible-playbook " + CREATE_NS_SCRIPT + " -e ns_name="+transitNS+" -e hypervisorIP="+hypervisorIP+" -e transitIP="+transitIP+" -e hypervisor="+config['tenant']['hypervisorType']
    subprocess.call([command], shell=True)
    logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Creating Transit VPC : " + command + "\n")

def deleteTransit(config, logFile):
    print('Deleting transit VPC')
    transitNS = str(config['tenant']['tenant_name'])+'_transit'
    command = "sudo ansible-playbook " + DELETE_NS_SCRIPT + " -e ns_name="+transitNS+" -e hypervisor="+config['tenant']['hypervisorType']
    subprocess.call([command], shell=True)
    logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Deleting Transit VPC : " + command + "\n")

def createIP(prefix, suffix):
    return (3*(prefix+'.'))+suffix

def checkYaml(yFile):
    if 'tenant' in yFile:
        if 'tenant_id' in yFile['tenant'] and 'tenant_name' in yFile['tenant'] and 'hypervisorType' in yFile['tenant']:
            return 0
    return 1

def main():
 
    fileName = "/var/log/log_"+time.strftime("%Y%m%d")+".txt"
    logFile = open(fileName, 'a+')

    if(len(sys.argv)<2):
        logging.error("ERROR: No arguments given")
        logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   No Arguments :"+ str(sys.argv)+"\n")
        exit(0)
    else:
        yFileName = sys.argv[2]
        # check if yaml file is passed
        if yFileName.endswith(".yml") or yFileName.endswith(".yaml"):
            try:
                # open the yaml file
                yFile = read_yaml_data(yFile)
                flag = checkYaml(yFile)
                if flag == 1:
                    logging.error("Incompatible YAML file")
                    logFile.write(time.strftime("%Y%m%d-%H%M%S")+"  Incompatible YAML File :"+ str(sys.argv)+"\n")
                    exit(0)
                # check for the 1st argument i.e., create or delete
                if str(sys.argv[1]).lower() == "delete":
                    print("Performing delete operation depending upon the file")
                    deleteTransit(yFile, logFile)

                elif str(sys.argv[1]).lower() == "create":
                    print("Performing create operation depending upon the file")
                    createTransit(yFile, logFile)
                else:
                    logging.error("ERROR: Unrecognized Command!!!")
                    exit(0)
            except Exception as ex:
                logging.error(str(ex))
                exit(0)
        else:
            logging.error("ERROR: No yaml/yml file found!!!")
            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   No YAML found :"+ str(sys.argv)+"\n")
            exit(0)
    logFile.close()


if __name__ == '__main__':
    main()
