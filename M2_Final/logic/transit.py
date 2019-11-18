import sys
import yaml
import logging
import subprocess

def createTransit(yFile, yFileName):
    #print('sudo ansible-playbook create transit.yaml -e file='+ yFileName +' -vvv')
    command = 'sudo ansible-playbook create_transit.yaml -e file='+ yFileName +' -vvv'
    command = command.split(' ')
    result = subprocess.run(command, stdout=subprocess.PIPE)
    result = result.stdout.decode('utf-8')
    result = result.split("\n")
    print(result[-3])
    if 'failed=0' in result[-3]:
        f1 = open('fileNS.txt','a')
        f1.write(yFile['tenant']['tenant_name']+'_transit\n')
        f2 = open('fileIP.txt','a')
        tenantID = str(yFile['tenant']['tenant_id'])
        f2.write(tenantID+'.'+tenantID+'.'+tenantID+'.'+'1\n')
        f2.write(tenantID+'.'+tenantID+'.'+tenantID+'.'+'2\n')
        f1.close()
        f2.close()
 

def deleteTransit(yFile):
    #print('sudo ip netns del '+ str(yFile['tenant']['tenant_name'])+'_transit')
    subprocess.call(['sudo ip netns del '+ str(yFile['tenant']['tenant_name'])+'_transit'], shell=True)

def checkYaml(yFile):
    if 'tenant' in yFile:
        if 'tenant_id' in yFile['tenant'] and 'tenant_name' in yFile['tenant']:
            try:
                f1 = open('fileNS.txt','r')
                for ns in f1:
                    if ns==yFile['tenant']['tenant_name']+'_transit'
                        print("this")
                        return(1)
                f2 = open('fileIP.txt','r')
                tid = str(yFile['tenant']['tenant_id'])
                t_ip1  = tid+'.'+tid+'.'+tid+'.'+'1'
                t_ip2  = tid+'.'+tid+'.'+tid+'.'+'2'
                for ip in f2:
                    if ip==t_ip1 or ip==t_ip2:
                        f2.close()
                        return(1)
                return(0)
            except:
                return(0)
    return(1)


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
                createTransit(yFile, yFileName)
            else:
                logging.error("ERROR: Unrecognized Command!!!")
                exit(0)
        except Exception as ex:
            logging.error(str(ex))
            exit(0)
    else:
        logging.error("ERROR: No yaml/yml file found!!!")
        exit(0)


