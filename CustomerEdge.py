import sys
import yaml
import logging
import subprocess

def createFunc(yFile, yFileName):
    if yFile['cloud']=="pri":
        subprocess.call(["sudo ansible-playbook createCENSNet.yaml -e file=" + yFileName + " -vvv"],shell=True)
        subprocess.call(["sudo ansible-playbook createCEVM.yaml -e file=" + yFileName + " -vvv"],shell=True)
    elif yFile['cloud']=="sec":
        subprocess.call(["sudo ansible-playbook createCENSNet_hyp.yaml -e file=" + yFileName + " -vvv"],shell=True)
        subprocess.call(["sudo ansible-playbook createCEVM_hyp.yaml -e file=" + yFileName + " -vvv"],shell=True)

def deleteFunc(yFile):
    print("executing delete")
    if yFile['cloud']=="pri":
        if "vms" in yFile:
            for i in range(len(yFile["vms"])):
                print(str(yFile["vms"][i]["vmName"]))
                subprocess.call(["sudo bash deleteVM.sh "+str(yFile["vms"][i]["vmName"])],shell=True)
                subprocess.call(["sudo bash deleteNet.sh "+str(yFile["siteNS"])+str(yFile["vms"][i]["vmName"])+"_CENSnet " +"t"+ str(yFile["tenantID"])+"s"+str(yFile["siteID"])+"v"+str(yFile["vms"][i]["vmName"])+"br"],shell=True)
    elif yFile['cloud']=='sec':
        subprocess.call(["sudo ansible-playbook deleteVM_hyp.yaml -e file=" + yFileName + " -vvv"],shell=True)
        subprocess.call(["sudo ansible-playbook deleteNet_hyp.yaml -e file=" + yFileName + " -vvv"],shell=True)

def checkYAML(yFile):
    if not ("vms" in yFile or "cloud" in yFile):
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
