import sys
import yaml
import logging
import subprocess
import time

def createFunc(yFile, yFileName, logFile):
    if yFile['cloud']=="pri":
        subprocess.call(["sudo ansible-playbook createCEVM.yaml -e file=" + yFileName + " -vvv"],shell=True)
        subprocess.call(["sudo ansible-playbook createCENSnet.yaml -e file=" + yFileName + " -vvv"],shell=True)
        if "vms" in yFile:
            for i in range(len(yFile["vms"])):
                logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Creating Customer Edge: "+ str(str(yFile["vms"][i]["vmName"]))+"\n")

    elif yFile['cloud']=="sec":
        subprocess.call(["sudo ansible-playbook createCEVM_hyp.yaml -e file=" + yFileName + " -vvv"],shell=True)
        subprocess.call(["sudo ansible-playbook createCENSnet_hyp.yaml -e file=" + yFileName + " -vvv"],shell=True)
        logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Creating Secondary Edge: "+"\n")


def deleteFunc(yFile, logFile):
    print("executing delete")
    if yFile['cloud']=="pri":
        if "vms" in yFile:
            for i in range(len(yFile["vms"])):
                print(str(yFile["vms"][i]["vmName"]))
                logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Deleting Customer Edge: "+ str(str(yFile["vms"][i]["vmName"]))+"\n")
                subprocess.call(["sudo bash deleteVM.sh "+str(yFile["siteNS"])+str(yFile["vms"][i]["vmName"])],shell=True)
                subprocess.call(["sudo bash deleteNet.sh "+str(yFile["siteNS"])+str(yFile["vms"][i]["vmName"])+"_CENSnet " +"t"+ str(yFile["tenantID"])+"s"+str(yFile["siteID"])+"v"+str(yFile["vms"][i]["vmName"])+"br"],shell=True)
    elif yFile['cloud']=='sec':
        subprocess.call(["sudo ansible-playbook deleteVM_hyp.yaml -e file=" + yFileName + " -vvv"],shell=True)
        subprocess.call(["sudo ansible-playbook deleteNet_hyp.yaml -e file=" + yFileName + " -vvv"],shell=True)

def checkYAML(yFile, logFile):
    if not ("vms" in yFile['site'] or "cloud" in yFile['site']):
        logging.error("\nERROR: Cannot perform create operation!!!")
        exit(0)

def main():

    fileName = "/var/log/log_"+time.strftime("%Y%m%d")+".txt"
    logFile = open(fileName, 'a+')

    if(len(sys.argv)<2):
        logging.error("\nERROR: less than 2 arguments given!!! Require 2 arguments to run")
        logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   ERROR: less than 2 arguments given!!! Require 2 arguments to run: "+ str(sys.argv)+"\n")
        exit(0)
    else:
        yFileName = sys.argv[2]
        # check if yaml file is passed
        if yFileName.endswith(".yml") or yFileName.endswith(".yaml"):
            try:
                #open the yaml file
                with open(yFileName,'r') as file:
                    yFile = yaml.load(file)
                checkYAML(yFile, logFile)
                # check for the 1st argument i.e., create or delete
                if str(sys.argv[1]).lower()=="delete":
                    print("\nPerforming delete operation depending upon the file")
                    deleteFunc(yFile['site'], logFile)
                elif str(sys.argv[1]).lower()=="create":
                    logging.info("\nPerforming create operation depending upon the file")
                    createFunc(yFile['site'],yFileName, logFile)
                else:
                    logging.error("\nERROR: Unrecognized Command!!!")
                    logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   ERROR: Unrecognized Command!!! "+ str(sys.argv)+"\n")
                    exit(0)
            except Exception as ex:
                logging.error(str(ex))
                exit(0)
        else:
            logging.error("\nERROR: No yaml/yml file found!!!")
            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   ERROR: less than 2 arguments given!!! Require 2 arguments to run: "+ str(sys.argv)+"\n")
            exit(0)
    logFile.close()

if __name__ == '__main__':
    main()

