import sys
import yaml
import logging
import subprocess

def createTransit(yFileName):
    #print('sudo ansible-playbook create transit.yaml -e file='+ yFileName +' -vvv')
    subprocess.call(['sudo ansible-playbook create_transit.yaml -e file='+ yFileName +' -vvv'], shell=True)

def deleteTransit(yFile):
    print('Deleting transit namespace')
    subprocess.call(['sudo ip netns del '+ str(yFile['tenant']['tenant_name'])+'_transit'], shell=True)
    print('Deleting the veth pair to hypervisor')
    subprocess.call(['sudo ip link set dev '+ str(yFile['tenant']['tenant_name'])+'_pub down'], shell=True)
    subprocess.call(['sudo ip link del '+ str(yFile['tenant']['tenant_name'])+'_pub'], shell=True)


def checkYaml(yFile):
    if 'tenant' in yFile:
        if 'tenant_id' in yFile['tenant'] and 'tenant_name' in yFile['tenant']:
            return 0
    return 1

def main():
 
    fileName = "/var/tmp/logs/log_"+time.strftime("%Y%m%d")+".txt"
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
                with open(yFileName, 'r') as file:
                    yFile = yaml.load(file)
                flag = checkYaml(yFile)
                if flag == 1:
                    logging.error("Incompatible YAML file")
                    logFile.write(time.strftime("%Y%m%d-%H%M%S")+"  Incompatible YAML File :"+ str(sys.argv)+"\n")
                    exit(0)
                # check for the 1st argument i.e., create or delete
                if str(sys.argv[1]).lower() == "delete":
                    print("Performing delete operation depending upon the file")
                    deleteTransit(yFile)
                    logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Delete Transit VPC :"+ str(yFile['tenant']['tenant_name'])+'_transit']+"\n")
                elif str(sys.argv[1]).lower() == "create":
                    print("Performing create operation depending upon the file")
                    createTransit(yFileName)
                    logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Create Transit VPC :"+ str(yFile['tenant']['tenant_name'])+'_transit']+"\n")
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
