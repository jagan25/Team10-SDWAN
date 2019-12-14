import sys
import yaml
import logging
import subprocess

def createFunc(yFile,yFileName):
    if(yFile['tenant']['changeNS'].lower() == 'y'):
        subprocess.call(["sudo ansible-playbook createSiteNS.yaml -e file=" + yFileName + " -vvv"],shell=True)
    if('router' in yFile):
        subprocess.call(["sudo ansible-playbook createInternalRouter.yaml -e file=" + yFileName + " -vvv"],shell=True)

def deleteFunc(yFile,yFileName):
    if('router' in yFile):
        subprocess.call(["sudo ansible-playbook deleteInternalRouter.yaml -e file=" + yFileName + " -vvv"],shell=True)
    if(yFile['tenant']['changeNS'].lower() == 'y'):
        subprocess.call(["sudo ansible-playbook deleteSiteNS.yaml -e file=" + yFileName + " -vvv"],shell=True)

def checkYAML(yaml):
    if 'tenant' not  in yaml:
        print("ERROR!!! Not in correct format!!!")
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
                deleteFunc(yFile,yFileName)
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
