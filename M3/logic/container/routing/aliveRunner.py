import sys
import os 
import subprocess

#import ansible_runner
import operator
import time
import requests
import yaml
import json

def read_yaml_data(f_name):
  data = None
  with open(f_name) as stream:
    data = yaml.safe_load(stream)
  return data


def write_yaml_data(data, f_name):
  with open(f_name, 'w') as outfile:
    yaml.dump(data, outfile)

def checkStatus(logFile):

    providerEdgeList = {}
    customerEdgeList = {}

    provider_data = read_yaml_data("provider_edges_config.yaml")
    customer_data = read_yaml_data("customer_edges_config.yaml")

    for provider in provider_data["ProviderEdges"]:
      providerEdgeList[provider_data["ProviderEdges"][provider]["ip"]] = provider
   

    for customer in customer_data["CustomerEdges"]:
      customerEdgeList[customer_data["CustomerEdges"][customer]["ip"]] = customer

    with open('aliveStatus.txt',"r+") as f:
        fileData = json.load(f)
        for p in fileData['status']:
            
            if float(p['lastPing']) < time.time()-60:
                print("CHANGE " + str(p['ip']))
                #check with the name for the CE
                

                #subprocess and check if it is down

                output = subprocess.check_output("ANSIBLE_STDOUT_CALLBACK=oneline ansible-playbook -i hosts ansibleVM.yaml -e 'container=LC1'", shell=True)
                #print(output)
                if "true" in str(output):
                   #see if new vms have to be spun up
                   print("O")


                else:
                    #restart the docker
                    output = subprocess.check_output("ANSIBLE_STDOUT_CALLBACK=oneline ansible-playbook -i hosts ansibleDockerStart.yaml -e 'container=LC6'", shell=True)
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