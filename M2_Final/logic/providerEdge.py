import sys
import yaml
import logging
import subprocess

def createPE(yFile, yFileName):
    print("creating pe")
    if "IPrange" in yFile:
        subprocess.call(["sudo ansible-playbook create_PEnetwork.yaml -e file=" + yFileName + " -vvv"], shell=True)
    if "vms" in yFile:
        subprocess.call(["sudo ansible-playbook create_PE.yaml -e file=" + yFileName + " -vvv"], shell=True)

def deletePE(yFile):
    print("deleting pe")
    if "vms" in yFile:
        for i in range(len(yFile["vms"])):
            print(str(yFile["vms"][i]["vmName"]))
            subprocess.call(["sudo bash deleteVM.sh " + str(yFile["tenant_name"])+"_"+(yFile["vms"][i]["vmName"])], shell=True)
    if "IPrange" in yFile:
        subprocess.call(["sudo bash deleteNet.sh" + str(yFile["tenant_name"])+"_PEnet "+ str(yFile["tenant_name"])+"_PEnet "],shell=True)

def checkYaml(yFile):
    if not 'IPrange' in yFile or not 'vms' in yFile:
        print("ERROR!!! Cannot process the given YAML file. MISSING KEYS!!!")
        exit(0)

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
            checkYaml(yFile)
            # check for the 1st argument i.e., create or delete
            if str(sys.argv[1]).lower() == "delete":
                print("Performing delete operation depending upon the file")
                deletePE(yFile)
            elif str(sys.argv[1]).lower() == "create":
                print("Performing create operation depending upon the file")
                createPE(yFile, yFileName)
        except:
            print("ERROR!!!")
