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
    if 'vms' in yFile:
        for i in range(len(yFile['vms'])):
            print(str(yFile['vms'][i]['PE_name']))
            subprocess.call(["sudo bash deleteVM.sh " + str(yFile["tenant_name"])+"_"+(yFile["vms"][i]["PE_name"])], shell=True)
    if 'IPrange' in yFile:
        print(yFile)
        subprocess.call(["sudo bash deletePENet.sh " + str(yFile["tenant_name"])],shell=True)

def checkYaml(yFile):
    if 'PE' not in yFile:
        print("ERROR!!! Missing 'PE' key in YAML file")
        exit(0)
    if not 'IPrange' in yFile['PE'] and not 'vms' in yFile['PE']:
        print("ERROR!!! Cannot process the given YAML file. MISSING KEYS!!!")
        exit(0)

if(len(sys.argv)<2):
    logging.error("ERROR: No arguments given")
    exit(0)

else:
    yFileName = sys.argv[2]
    # print(yFileName)
    # check if yaml file is passed
    if yFileName.endswith(".yml") or yFileName.endswith(".yaml"):
        try:
            # open the yaml file
            with open(yFileName, 'r') as file:
                yFile = yaml.load(file)
            #print(yFile)
            checkYaml(yFile)
            # check for the 1st argument i.e., create or delete
            if str(sys.argv[1]).lower() == "delete":
                print("Performing delete operation depending upon the file")
                deletePE(yFile['PE'])
            elif str(sys.argv[1]).lower() == "create":
                print("Performing create operation depending upon the file")
                createPE(yFile['PE'], yFileName)
        except:
            print("ERROR!!!")
