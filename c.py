import sys
import yaml
import logging
import subprocess
import time

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
        subprocess.call(["sudo bash deleteContNet.sh "+str(yFile["tenantID"])],shell=True)


def checkYAML(yFile, logFile):
    if not "tenantInfo" in yFile:
        logging.error("\nERROR: Cannot perform create operation!!!")
        logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Tenant Id missing in yaml file : "+ str(sys.argv)+"\n")
        exit(0)
    if not ("vms" in yFile['tenantInfo'] or "controllerNet" in yFile['tenantInfo']):
        logging.error("\nERROR: Cannot perform create operation!!!")
        logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Wrong config in yaml file : "+ str(sys.argv)+"\n")
        exit(0)

def main():
  #file = sys.argv[1]
  #createVPC(file)
  fileName = "/tmp/logs/log_"+time.strftime("%Y%m%d")+".txt"
  logFile = open(fileName, 'a+')

  if(len(sys.argv)<2):
        logging.error("\nERROR: less than 2 arguments given!!! Require 2 arguments to run")
        logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Argument Length Error: "+ str(sys.argv)+"\n")
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
                    deleteFunc(yFile["tenantInfo"])
                    logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Deleting Controller : "+ str(yFile["vms"][i]["vmName"])+"\n")
                elif str(sys.argv[1]).lower()=="create":
                    logging.info("\nPerforming create operation depending upon the file")
                    createFunc(yFile["tenantInfo"],yFileName)
                    logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Creating Controller : "+ str(yFile["vms"][i]["vmName"])+"\n")

                else:
                    logging.error("\nERROR: Unrecognized Command!!!")
                    logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Wrong Command : "+ str(sys.argv)+"\n")
                    exit(0)
            except Exception as ex:
                logging.error(str(ex))
                exit(0)
        else:
            logging.error("\nERROR: No yaml/yml file found!!!")
            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   No yaml/yml file found : "+ str(sys.argv)+"\n")
            exit(0)
  logFile.close()



if __name__ == '__main__':
    main()
