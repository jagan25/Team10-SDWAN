import sys
import os 
import subprocess

#import ansible_runner
import operator
import time
import requests
import yaml
import json

CONFIG_FOLDER_PATH = '/etc/config/container/'
ANSIBLE_FOLDER_PATH = '/var/scripts/container/'
HOSTS_FILE = CONFIG_FOLDER_PATH+"hosts"
CONTAINER_STATUS_SCRIPT = ANSIBLE_FOLDER_PATH+"ansibleVM.yaml"
DOCKER_RESTART_SCRIPT = ANSIBLE_FOLDER_PATH+"ansibleDockerStart.yaml"
PROVIDER_EDGES_CONFIG_FILE = CONFIG_FOLDER_PATH+"PEConfig.txt"
CUSTOMER_EDGES_CONFIG_FILE = CONFIG_FOLDER_PATH+"CEConfig.txt"
ALIVE_STATUS_FILE = CONFIG_FOLDER_PATH+"aliveStatus.txt"

def read_yaml_data(f_name):
  data = None
  with open(f_name) as stream:
    data = json.load(stream)
  return data

def write_yaml_data(data, f_name):
  with open(f_name, 'w') as outfile:
    yaml.dump(data, outfile)

def checkStatus(logFile):

    providerEdgeList = {}
    customerEdgeList = {}

    provider_data = read_yaml_data(PROVIDER_EDGES_CONFIG_FILE)
    customer_data = read_yaml_data(CUSTOMER_EDGES_CONFIG_FILE)

    
    for key, provider in enumerate(provider_data["ProviderEdges"]):
        for pr in provider:
           providerEdgeList[provider[pr]["ip"]] = pr

    for key, customer in enumerate(customer_data["CustomerEdges"]):
        for cr in customer:
           customerEdgeList[customer[cr]["ip"]] = cr


    with open(ALIVE_STATUS_FILE,"r+") as f:
        fileData = json.load(f)
        for p in fileData['status']:
            
            if float(p['lastPing']) < time.time()-60:
                print("CHANGE " + str(p['ip']))
                #check with the name for the CE
                

                #subprocess and check if it is down

                output = subprocess.check_output("ANSIBLE_STDOUT_CALLBACK=oneline ansible-playbook " + CONTAINER_STATUS_SCRIPT + " -e 'container=+'p['name']", shell=True)
                #print(output)
                if "true" in str(output):
                   #see if new vms have to be spun up
                   print("O")


                else:
                    #restart the docker
                    output = subprocess.check_output("ANSIBLE_STDOUT_CALLBACK=oneline ansible-playbook " + DOCKER_RESTART_SCRIPT + " -e 'container='+p['name']", shell=True)
                    print(output)
                    #the instance is down

                #after making it up
                #write to log file as well
                p['lastPing'] = time.time()

                
        f.seek(0)
        f.truncate()
        json.dump(fileData, f)

    f.close()   


def main():
  #file = sys.argv[1]
  #createVPC(file)
  fileName = "/tmp/logs/log_"+time.strftime("%Y%m%d")+".txt"
  logFile = open(fileName, 'a+')
  checkStatus(logFile)


if __name__ == '__main__':
    main()
