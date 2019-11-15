import sys
import yaml
import logging
import subprocess

def createFunc(yFile):
    if "contNetwork" in yFile:
        subprocess.call(["sudo ansible-playbook createControllerNetwork.yaml -vvvvv"],shell=True)
    if "vms" in yFile:
        subprocess.call(["sudo ansible-playbook createControllerVM.yaml -vvvvv"],shell=True)

def deleteFunc(yFile):
    print("executing delete")
    if "vms" in yFile:
        for i in range(len(yFile["vms"])):
            print(str(yFile["vms"][i]["vmName"]))
            subprocess.call(["sudo bash deleteController.sh "+str(yFile["vms"][i]["vmName"])],shell=True)
    if "contNetwork" in yFile:
        subprocess.call(["sudo bash deleteControllerNet.sh "+str(yFile["vxlanID"])+" "+str(yFile["contNetwork"])+" "+str(yFile["vethPair1"])],shell=True)


def checkYAMLcreate(yFile):
    if not ("vms" in yFile or "contNetwork" in yFile):
        logging.error("\nERROR: Cannot perform create operation!!!")
        exit(0)



if(len(sys.argv)<2):
    logging.error("\nERROR: less than 2 arguments given!!! Require 2 arguments to run")
    exit(0)
else:
    yFileName = sys.argv[2]
    # check if yaml file is passed
    if yFileName.endswith(".yml") or yFileName.endswith(".yaml"):
        try:
            #open the yaml file
            with open(yFileName,'r') as file:
                yFile = yaml.load(file)

            # check for the 1st argument i.e., create or delete
            if str(sys.argv[1]).lower()=="delete":
                print("\nPerforming delete operation depending upon the file")
                deleteFunc(yFile)
            elif str(sys.argv[1]).lower()=="create":
                logging.info("\nPerforming create operation depending upon the file")
                createFunc(yFile)
            else:
                logging.error("\nERROR: Unrecognized Command!!!")
                exit(0)
        except Exception as ex:
            logging.error(str(ex))
            exit(0)
    else:
        logging.error("\nERROR: No yaml/yml file found!!!")
        exit(0)
