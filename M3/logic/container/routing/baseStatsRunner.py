import yaml
import sys
import os 
import ansible_runner
import operator
import time
#nproc
#ip- load, cpus. flag
providerEdgeChange = {}

#ip- load, cpus
customerEdgeChange = {}

customerProviderMapping = {}

availableProvider = []
heavyProvider = []

IP_FILE = "hostVars.yaml"
ROUTE_FILE = "changeRouteVars.yaml"
TRANSIT_FILE = "changeTransitVars.yaml"
CPU_LOAD_SCRIPT = "ansi.yaml"
ROUTE_CHANGE_SCRIPT = "changeDefaultRoute.yaml"
PROVIDER_EDGES_CONFIG_FILE = "provider_edges_config.yaml"
CUSTOMER_EDGES_CONFIG_FILE = "customer_edges_config.yaml"


def readStatsFile():
  filepath = 'statsLoader.txt'
  statsMap = {}
  with open(filepath) as fp:
     line = fp.readline()
     while line:
         line = line.split(" ")
         statsMap[name] = line[0]
         statsMap[name]['cpus'] = int(line[1])
         statsMap[name]['load'] = float(line[2])
         statsMap[name]['flag'] = line[3]
         
  return statsMap


def run_ansible_script(logFile):
  # Refer https://ansible-runner.readthedocs.io/en/latest/python_interface.html for ansible doc
  
  provider_data = read_yaml_data("provider_edges_config.yaml")
  customer_data = read_yaml_data("customer_edges_config.yaml")
  transit_data = read_yaml_data("transit_edges_config.yaml")
  providerList = {}
  customerEdgeList = {}


  for provider in provider_data["ProviderEdges"]:
      providerList[provider] = provider_data["ProviderEdges"][provider]["ip"]
      if(len(provider_data["ProviderEdges"][provider]["customer_edges"]))>0:
        for i in provider_data["ProviderEdges"][provider]["customer_edges"]:
          customerProviderMapping[i] = provider
      

  for customer in customer_data["CustomerEdges"]:
      customerEdgeList[customer] = customer_data["CustomerEdges"][customer]["ip"]

  print(providerList)
  print(customerEdgeList)
  
  customerLoad = {}
  providerLoad = {}

  playbook_path = os.getcwd()
  changeFlag = False
  
  ##read stats file
  statsMap = readStatsFile()

  # r = ansible_runner.run(private_data_dir=playbook_path, playbook='ansible.yaml')
  # out = r.get_fact_cache("50.0.0.217")
  # print(out['output'])

  #playbook_path = playbook_path.replace("north_bound", "ansible_scripts")
  for name in providerList:
    #store in that file
    #ip_data = {"host": providerList[name]}
    #write_yaml_data(ip_data, IP_FILE)

    providerEdgeChange[name]={}
    #r = ansible_runner.run(private_data_dir=playbook_path, playbook='ansi.yaml')
    #out = r.get_fact_cache(providerList[name])
    #retVal = out['output'].split(" ")
    providerEdgeChange[name]['load'] = statsMap[name]['load']
    providerEdgeChange[name]['cpus'] = statsMap[name]['cpus']
    providerEdgeChange[name]['flag'] = statsMap[name]['flag']
    logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   PE(load): "+ name+" :"+str(statsMap[name]['load'])+"\n")
    if retVal[2]=="TRUE":
      changeFlag = True
    
  if changeFlag:

    transitCustomerEdgeMap = {}
 
    for i in transit_data["Transit_Edges"]:
        transitCustomerEdgeMap[i] = transit_data["Transit_Edges"][i]

    print("TRANSIT MAP" + str(transitCustomerEdgeMap))

    for name in customerEdgeList:
      #store in that file
      customerEdgeChange[name]={}

      #ip_data = {"host": customerEdgeList[name]}
      #write_yaml_data(ip_data, IP_FILE)

      #r = ansible_runner.run(private_data_dir=playbook_path, playbook='cpuUsage.yaml')
      #out = r.get_fact_cache(customerEdgeList[name])
      #retVal = out['output'].split(" ")
      customerEdgeChange[name]['load'] = statsMap[name]['load']
      customerEdgeChange[name]['cpus'] = statsMap[name]['cpus']
      customerEdgeChange[name]['flag'] = statsMap[name]['flag']
      logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   CE(load): "+ name+" :"+str(statsMap[name]['load'])+"\n")


    for i in customerEdgeChange:

      customerLoad[i] = customerEdgeChange[i]['load'] * customerEdgeChange[i]['cpus']

    customerLoad = dict(sorted(customerLoad.items(), key=operator.itemgetter(1), reverse = True))


    for i in providerEdgeChange:
      providerLoad[i] = (100-providerEdgeChange[i]['load']) * providerEdgeChange[i]['cpus']
      if  providerEdgeChange[i]['flag'] == "FALSE":
        availableProvider.append(i)
      else:
        heavyProvider.append(i) 

    providerLoad = dict(sorted(providerLoad.items(), key=operator.itemgetter(1), reverse = True))

    # # for prov in heavyProvider:
    #   #check customerEdge:
    #   customerEdges = customerProviderMapping[prov]
      #sort customer Edges
    print("availableProvider" + str(availableProvider))
    print("heavyProvider" + str(heavyProvider))

    for cust in customerLoad:
      # only for pe changes
      
      if customerProviderMapping[cust] in heavyProvider:

        cLoad = customerLoad[cust] 

        for prov in providerLoad:
          #check available provider
          if prov in availableProvider:

            if cLoad < ((providerEdgeChange[prov]['cpus']*0.6*100)-(providerEdgeChange[prov]['cpus']*100-providerLoad[prov])):
              #logic to add to provider - call ssh 

              existing_if = customer_data["CustomerEdges"][cust]["provider_edges"][customerProviderMapping[cust]]
              new_if = customer_data["CustomerEdges"][cust]["provider_edges"][prov]
              
              #add the things to file
              route_data = {"ip": customerEdgeList[name], "oldInterface": existing_if, "newInterface": new_if}
              logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Transit PE-CE(update): CE= "+ cust+" OLD PE= "+ customerProviderMapping[cust]+" NEW PE= "+prov+ " COMMAND = "+str(route_data)+"\n")
              write_yaml_data(route_data, ROUTE_FILE)
              
              r = ansible_runner.run(private_data_dir=playbook_path, playbook='changeDefaultRoute.yaml')

              #change in transit route as well
              existing_if = transitCustomerEdgeMap[customerProviderMapping[cust]]
              new_if = transitCustomerEdgeMap[prov]
              cNetworks=[]


              route_data = {}
              count=0
              for cn in customer_data["CustomerEdges"][cust]["cnetwork"]:
                cNetworks.append(customer_data["CustomerEdges"][cust]["cnetwork"][cn])
                route_data[count] = {}
                route_data[count]["source"] = customer_data["CustomerEdges"][cust]["cnetwork"][cn]
                route_data[count]["oldInterface"] = existing_if
                route_data[count]["newInterface"] = new_if
                route_data[count]["netnsName"] = transit_data["TransitName"]
                count+=1

              print(route_data)

              logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   PE-CE(update): CE= "+ cust+" OLD PE= "+ customerProviderMapping[cust]+" NEW PE= "+prov+ " COMMAND = "+str(route_data)+"\n")
              write_yaml_data(route_data, TRANSIT_FILE)
              
              r = ansible_runner.run(private_data_dir=playbook_path, playbook='changeTransitRoute.yaml')

              #change in config files
              provider_data["ProviderEdges"][customerProviderMapping[cust]]["customer_edges"].remove(cust)
              provider_data["ProviderEdges"][prov]["customer_edges"].append(cust)
              providerLoad[prov] = (providerLoad[prov] - cLoad)
              providerLoad = dict(sorted(providerLoad.items(), key=operator.itemgetter(1), reverse = True))
              # change customerProviderMapping
              customerProviderMapping[cust] = prov
              break

    write_yaml_data(provider_data, "provider_edges_config.yaml")
  logFile.close()

def read_yaml_data(f_name):
  data = None
  with open(f_name) as stream:
    data = yaml.safe_load(stream)
  return data


def write_yaml_data(data, f_name):
  with open(f_name, 'w') as outfile:
    yaml.dump(data, outfile)


def createVPC(file):
  data = read_yaml_data(file)
  print(data)
  #vpc_data = read_yaml_data(VPC_FILE)

  #valid = validateInput(data, vpc_data)


def main():
  #file = sys.argv[1]
  #createVPC(file)
  fileName = "/tmp/logs/log_"+time.strftime("%Y%m%d")+".txt"
  logFile = open(fileName, 'a+')
  run_ansible_script(logFile)


if __name__ == '__main__':
    main()
