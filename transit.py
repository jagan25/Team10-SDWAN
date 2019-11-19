import sys
import yaml
import logging
import subprocess

def createTransit(yFileName):
    #print('sudo ansible-playbook create transit.yaml -e file='+ yFileName +' -vvv')
    subprocess.call(['sudo ansible-playbook create_transit.yaml -e file='+ yFileName +' -vvv'], shell=True)

def deleteTransit(yFile):
    #print('sudo ip netns del '+ str(yFile['tenant']['tenant_name'])+'_transit')
    subprocess.call(['sudo ip netns del '+ str(yFile['tenant']['tenant_name'])+'_transit'], shell=True)

def checkYaml(yFile):
    if 'tenant' in yFile:
        if 'tenant_id' in yFile['tenant'] and 'tenant_name' in yFile['tenant']:
            return 0
    return 1


if(len(sys.argv)<2):
    logging.error("ERROR: No arguments given")
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
                exit(0)
            # check for the 1st argument i.e., create or delete
            if str(sys.argv[1]).lower() == "delete":
                print("Performing delete operation depending upon the file")
                deleteTransit(yFile)
            elif str(sys.argv[1]).lower() == "create":
                print("Performing create operation depending upon the file")
                createTransit(yFileName)
            else:
                logging.error("ERROR: Unrecognized Command!!!")
                exit(0)
        except Exception as ex:
            logging.error(str(ex))
            exit(0)
    else:
        logging.error("ERROR: No yaml/yml file found!!!")
        exit(0)


