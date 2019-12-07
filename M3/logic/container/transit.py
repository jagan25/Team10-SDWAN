import sys
import yaml
import logging
import subprocess
import time

CONFIG_FOLDER_PATH = '/etc/config/container/'
ANSIBLE_FOLDER_PATH = '/var/scripts/container/'
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
    logging.info('Creating transit VPC')
    if config['tenant']['hypervisorType'] == 'primary':
        hypervisorIP = str(config['tenant']['tenant_id'])+ ".0.0.1"
        transitIP = str(config['tenant']['tenant_id'])+ ".0.0.2"
    elif config['tenant']['hypervisorType'] == 'secondary':
        hypervisorIP = str(config['tenant']['tenant_id'])+ ".255.0.1"
        transitIP = str(config['tenant']['tenant_id'])+ ".255.0.2"

    transitNS = str(config['tenant']['tenant_name'])+'_transit'#+str(config['tenant'])#['transit_id'])
    tunnel_name = "gre_"+config['tenant']['tenant_name']
    command = "sudo ansible-playbook " + CREATE_NS_SCRIPT + " -e ns_name="+transitNS+" -e hypervisorIP="+hypervisorIP+" -e option=transit -e transitIP="+transitIP+" -e hypervisor="+config['tenant']['hypervisorType']+" -e tunnel_name="+tunnel_name+" -e remoteIP="+str(config['tenant']['remote_ip'])
    subprocess.call([command], shell=True)
    logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Creating Transit VPC : " + command + "\n")

def deleteTransit(config, logFile):
    logging.info('Deleting transit VPC')
    transitNS = str(config['tenant']['tenant_name'])+'_transit'#+str(config['tenant']['transit_id'])
    command = "sudo ansible-playbook " + DELETE_NS_SCRIPT + " -e ns_name="+transitNS+" -e hypervisor="+config['tenant']['hypervisorType']
    subprocess.call([command], shell=True)
    logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Deleting Transit VPC : " + command + "\n")

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
                yFile = read_yaml_data(CONFIG_FOLDER_PATH + yFileName)
                flag = checkYaml(yFile)
                if flag == 1:
                    logging.error("Incompatible YAML file")
                    logFile.write(time.strftime("%Y%m%d-%H%M%S")+"  Incompatible YAML File :"+ str(sys.argv)+"\n")
                    exit(0)
                # check for the 1st argument i.e., create or delete
                if str(sys.argv[1]).lower() == "delete":
                    logging.info("Performing delete operation depending upon the file")
                    deleteTransit(yFile, logFile)

                elif str(sys.argv[1]).lower() == "create":
                    logging.info("Performing create operation depending upon the file")
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

