import sys
import yaml
import logging
import subprocess
import time

def createPE(yFile, yFileName):
    print("creating pe")
    if "IPrange" in yFile:
        subprocess.call(["sudo ansible-playbook create_PEnetwork.yaml -e file=" + yFileName + " -vvv"], shell=True)
        logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Creating IP Ranges for PE : "+ str(yFile["tenant_name"])+"\n")

    if "vms" in yFile:
        subprocess.call(["sudo ansible-playbook create_PE.yaml -e file=" + yFileName + " -vvv"], shell=True)
        for i in range(len(yFile['vms'])):
            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Creating PE : "+ str(yFile['vms'][i]['PE_name'])+"\n")


def deletePE(yFile, logFile):
    if 'vms' in yFile:
        for i in range(len(yFile['vms'])):
            print(str(yFile['vms'][i]['PE_name']))
            subprocess.call(["sudo bash deleteVM.sh " + str(yFile["tenant_name"])+"_"+(yFile["vms"][i]["PE_name"])], shell=True)
            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Deleting PE : "+ str(yFile["tenant_name"])+"_"+(yFile["vms"][i]["PE_name"]) +"\n")

    if 'IPrange' in yFile:
        print(yFile)
        subprocess.call(["sudo bash deletePENet.sh " + str(yFile["tenant_name"])],shell=True)
        logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Deleting IPRange for PE : "+ str(yFile["tenant_name"]) +"\n")


def checkYaml(yFile, logFile):
    if 'PE' not in yFile:
        print("ERROR!!! Missing 'PE' key in YAML file")
        logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   ERROR!!! Missing 'PE' key in YAML file : "+ str(sys.argv) +"\n")
        exit(0)
    if not 'IPrange' in yFile['PE'] and not 'vms' in yFile['PE']:
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
                with open(yFileName, 'r') as file:
                    yFile = yaml.load(file)
                #print(yFile)
                checkYaml(yFile)
                # check for the 1st argument i.e., create or delete
                if str(sys.argv[1]).lower() == "delete":
                    print("Performing delete operation depending upon the file")
                    deletePE(yFile['PE'], logFile)
                elif str(sys.argv[1]).lower() == "create":
                    print("Performing create operation depending upon the file")
                    createPE(yFile['PE'], yFileName, logFile)
            except:
                print("ERROR!!!")
                logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Error In Executing Command : "+ str(sys.argv) +"\n")
        else:
            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Error In Executing Command : "+ str(sys.argv) +"\n")
            
    logFile.close()

if __name__ == '__main__':
    main()

