import sys
import yaml
import logging
import subprocess

def createFunc(yFile, yFileName):
    if yFile['controllerNet'].lower()=="y":
        if yFile['cloud']=="pri":
            subprocess.call(["sudo ansible-playbook createControllerNetwork.yaml -e file=" + yFileName + " -vvv"],shell=True)
        elif yFile['cloud']=="sec":
            subprocess.call(["sudo ansible-playbook createControllerNetwork_hyp.yaml -e file=" + yFileName + " -vvv"],shell=True)
    if "vms" in yFile:
        subprocess.call(["sudo ansible-playbook createControllerVM.yaml -e file=" + yFileName + " -vvv"],shell=True)

def deleteFunc(yFile):
    print("executing delete")
    if "vms" in yFile:
        for i in range(len(yFile["vms"])):
            print(str(yFile["vms"][i]["vmName"]))
            subprocess.call(["sudo bash deleteVM.sh "+str(yFile["vms"][i]["vmName"])],shell=True)
    if yFile['controllerNet'].lower()=="y":
        subprocess.call(["sudo bash deleteNet.sh "+str(yFile["tenantID"])+"_controller_net " + str(yFile["tenantID"])+"_controllerbr"],shell=True)


def checkYAML(yFile):
    if not ("vms" in yFile or "controllerNet" in yFile):
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
            checkYAML(yFile)
            # check for the 1st argument i.e., create or delete
            if str(sys.argv[1]).lower()=="delete":
                print("\nPerforming delete operation depending upon the file")
                deleteFunc(yFile)
            elif str(sys.argv[1]).lower()=="create":
                logging.info("\nPerforming create operation depending upon the file")
                createFunc(yFile,yFileName)
            else:
                logging.error("\nERROR: Unrecognized Command!!!")
                exit(0)
        except Exception as ex:
            logging.error(str(ex))
            exit(0)
    else:
        logging.error("\nERROR: No yaml/yml file found!!!")
        exit(0)
