import yaml
import sys
import os
import json
import ansible_runner
import operator
import time
import subprocess
#nproc
#ip- load, cpus. flag
providerEdgeChange = {}

#ip- load, cpus
customerEdgeChange = {}

customerProviderMapping = {}

availableProvider = []
heavyProvider = []

CONFIG_FOLDER_PATH = '/etc/config/container/'
ANSIBLE_FOLDER_PATH = '/var/scripts/container/'
PROVIDER_EDGES_CONFIG_FILE = CONFIG_FOLDER_PATH+"PEConfig.txt"
CUSTOMER_EDGES_CONFIG_FILE = CONFIG_FOLDER_PATH+"CEConfig.txt"
TRANSIT_EDGES_CONFIG_FILE = CONFIG_FOLDER_PATH+"TPE_config.txt"
STATS_LOADER_FILE = CONFIG_FOLDER_PATH+"statsLoader.txt"
ROUTE_FILE = ANSIBLE_FOLDER_PATH+"changeRouteVars.yaml"
TRANSIT_FILE = ANSIBLE_FOLDER_PATH+"changeTransitVars.yaml"
ROUTE_CHANGE_SCRIPT = ANSIBLE_FOLDER_PATH+"changeDefaultRoute.yaml"

# See if PE has to be changed
# If PE is changed, then think about CE
# IF PE is not changed, think only about auto scaling

# this is because CE and PE can have different configurations

def readStatsFile():
  filepath = 'STATS_LOADER_FILE'
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
  
  provider_data = read_yaml_data("PROVIDER_EDGES_CONFIG_FILE")
  customer_data = read_yaml_data("CUSTOMER_EDGES_CONFIG_FILE")
  transit_data = read_yaml_data("TRANSIT_EDGES_CONFIG_FILE")
  providerList = {}
  customerEdgeList = {}
  customerEdgeCount = {}
  providerIdList = {}

  for key, provider in enumerate(provider_data["ProviderEdges"]):
      for pr in provider:
         providerList[pr] = provider[pr]["ip"]
         if "customer_edges" in provider["pr"] and len(customer["cr"]["customer_edges"])>0:
            for cr in provider["pr"]["customer_edges"]:
              customerProviderMapping[cr] = pr

  for key, customer in enumerate(customer_data["CustomerEdges"]):
      for cr in customer:
         customerEdgeList[cr] = customer[cr]["ip"]

  for key, customer in enumerate(customer_data["CECount"]):
      for cr in customer:
        customerEdgeCount[cr] = {}
        customerEdgeCount[cr]['max'] = customer[cr]['max']
        customerEdgeCount[cr]['min'] = customer[cr]['min']


  print(providerList)
  print(customerEdgeList)
  
  customerLoad = {}
  providerLoad = {}

  playbook_path = os.getcwd()
  providerChangeFlag = False
  customerChangeFlag = False
  
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
    
    providerLoad[name] = (100-providerEdgeChange[i]['load']) * providerEdgeChange[i]['cpus']

    if statsMap[name]['flag']=="TRUE":
     
      providerChangeFlag = True
      availableProvider.append(name)    
    
    else:
      
      heavyProvider.append(name) 

    
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
    customerLoad[name] = customerEdgeChange[name]['load'] * customerEdgeChange[name]['cpus']
    
    if statsMap[name]['flag']=="TRUE":
      customerChangeFlag = True


  # downgrade - intermittent VM
  for name in customerEdgeChange:

    if customerEdgeChange[name]["load"] < 20 and len({key for key in customerEdgeList.items()  
                  if key.startswith(customer.split("CE")[0])}) > 1:

        #auto scale
        currentPE = customerProviderMapping[name]
        #give this PE to customer

        deleteCEContainer(customer.split("CE")[0],currentPE, customer.split("CE")[1])
        output = subprocess.check_output("sudo python customerEdge.py create CEConfVar.yaml", shell = True)
        logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Down Scaling CE: "+name+"  PE = "+currentPE+"\n")
        
        # remove from customerredgelist
        customerEdgeList.remove(name)





  if providerChangeFlag == True or customerChangeFlag == True:
    providerLoad = dict(sorted(providerLoad.items(), key=operator.itemgetter(1), reverse = True))
    customerLoad = dict(sorted(customerLoad.items(), key=operator.itemgetter(1), reverse = True))

    if providerChangeFlag == False and customerChangeFlag == True:

      #only auto scaling
      for customer in customerEdgeChange:

        if customerEdgeChange[customer]['flag'] == "TRUE":
          # for autoscaling, we can give 
          if len({key for key in customerEdgeList.items()  
                  if key.startswith(customer.split("CE")[0])}) < customerEdgeCount[customer.split("CE")[0]]['max']:

            #auto scale
            currentPE = customerProviderMapping[currentContainers[0]]
            #give this PE to customer

            createCEContainer(customer.split("CE")[0],currentPE)
            output = subprocess.check_output("sudo python customerEdge.py create CEConfVar.yaml", shell = True)
            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Auto Scaling CE: "+customer.split("CE")[0]+"  PE = "+currentPE+"\n")

            

            #call sandeep function. When the return is success - add it to provider Mac
                   
            

            


  elif providerChangeFlag == True and customerChangeFlag == True:

    #both have to be done
    transitCustomerEdgeMap = {}
 
    for i in transit_data["Transit_Edges"]:
        transitCustomerEdgeMap[i] = transit_data["Transit_Edges"][i]

    for customer in customerEdgeChange:

      if customerEdgeChange[customer]['flag'] == "TRUE":
        #auto scaling if possible

        currentContainers = {key for key in customerEdgeList.items()  
                 if key.startswith(customer.split("CE")[0])}

        if len(currentContainers) < customerEdgeCount[customer.split("CE")[0]]['max']:
          #auto scale - else chuck

          #find how many autoscaling can be done
          numberOfAutoScaling = 1
          reduceLoad = (customerEdgeChange[customer]['load'] - 60) * len(currentContainers)
          while(reduceLoad)
          currentCELoad = 0
          for container in currentContainers:
              customerEdgeChange[name]['load'] = currentLoad[container] * ((len(currentContainers))/(len(currentContainers)+1))
              currentLoad[container] = currentLoad[container] * ((len(currentContainers))/len(currentContainers)+1)
              currentCELoad = customerEdgeChange[name]['load']

          customerLoad = dict(sorted(customerLoad.items(), key=operator.itemgetter(1), reverse = True))

          #now find a suitable PE for load
          currentPE = customerProviderMapping[currentContainers[0]]
          for pe in providerLoad:
            if pe in availableProvider and providerLoad[pe]>currentCELoad:
              currentPE = pe 
              providerLoad[pe] -= currentCELoad
              providerLoad = dict(sorted(providerLoad.items(), key=operator.itemgetter(1), reverse = True))
              break;

          #autoscale with currentPE and create a new instance
          
          #create CE and autoscale
          
          # add it to provider Edge file and customerEdge file
          createCEContainer(customer.split("CE")[0],currentPE)
          output = subprocess.check_output("sudo python customerEdge.py create CEConfVar.yaml", shell = True)
          logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Auto Scaling CE: "+customer.split("CE")[0]+"  PE = "+currentPE+"\n")

  
      

        # divide customerLoad

        #customerLoad[customer] = customerLoad[customer] - {{load}}
        #change it 

      #-----PE----------Dynamic Routing Change

    for cust in customerLoad:
    # only for pe changes
    
      if customerProviderMapping[cust] in heavyProvider:

        cLoad = customerLoad[cust] 

        for prov in providerLoad:
          #check available provider
          if prov in availableProvider:

            if cLoad < ((providerEdgeChange[prov]['cpus']*0.6*100)-(providerEdgeChange[prov]['cpus']*100-providerLoad[prov])):
              #logic to add to provider - call ssh 

              existing_if = None
              new_if = None
              for key, customer in enumerate(customer_data["CustomerEdges"]):
                for cr in customer:
                   if cust==cr:
                     for pe in customer[cr]["provider_edges"]:
                       if pe==customerProviderMapping[cust]:
                         existing_if = customer[cr]["provider_edges"][pe]
                       if pe==prov:
                         new_if = customer[cr]["provider_edges"][pe]
              
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
              for key, customer in enumerate(customer_data["CustomerEdges"]):
                for cr in customer:
                   if cr==cust:
                    for cn in customer[cr]["cnetwork"]:
                      route_data[count] = {}
                      route_data[count]["source"] = customer[cr]["cnetwork"][cn]
                      route_data[count]["oldInterface"] = existing_if
                      route_data[count]["newInterface"] = new_if
                      route_data[count]["netnsName"] = cr.split("ns")[0]+"_transit"
                      count+=1

              print(route_data)

              logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   PE-CE(update): CE= "+ cust+" OLD PE= "+ customerProviderMapping[cust]+" NEW PE= "+prov+ " COMMAND = "+str(route_data)+"\n")
              write_yaml_data(route_data, TRANSIT_FILE)
              
              r = ansible_runner.run(private_data_dir=playbook_path, playbook='changeTransitRoute.yaml')

              for key, provider in enumerate(provider_data["ProviderEdges"]):
                for i in range(len(provider)):

                   if provider_data["ProviderEdges"][i]==customerProviderMapping[cust]:
                    provider_data["ProviderEdges"][i][customerProviderMapping[cust]]["customer_edges"].remove(cust)

                   if provider_data["ProviderEdges"][i]==prov:
                    provider_data["ProviderEdges"][i][prov]["customer_edges"].append(cust)




              #change in config files
              # provider_data["ProviderEdges"][customerProviderMapping[cust]]["customer_edges"].remove(cust)
              # provider_data["ProviderEdges"][prov]["customer_edges"].append(cust)
 

              providerLoad[prov] = (providerLoad[prov] - cLoad)
              providerLoad = dict(sorted(providerLoad.items(), key=operator.itemgetter(1), reverse = True))
              # change customerProviderMapping
              customerProviderMapping[cust] = prov
              break

    

  else:

      #only PE Change

    for cust in customerLoad:
      # only for pe changes
      
      if customerProviderMapping[cust] in heavyProvider:

        cLoad = customerLoad[cust] 

        for prov in providerLoad:
          #check available provider
          if prov in availableProvider:

            if cLoad < ((providerEdgeChange[prov]['cpus']*0.6*100)-(providerEdgeChange[prov]['cpus']*100-providerLoad[prov])):
              #logic to add to provider - call ssh 

              existing_if = None
              new_if = None
              for key, customer in enumerate(customer_data["CustomerEdges"]):
                for cr in customer:
                   if cust==cr:
                     for pe in customer[cr]["provider_edges"]:
                       if pe==customerProviderMapping[cust]:
                         existing_if = customer[cr]["provider_edges"][pe]
                       if pe==prov:
                         new_if = customer[cr]["provider_edges"][pe]

              #existing_if = customer_data["CustomerEdges"][cust]["provider_edges"][customerProviderMapping[cust]]
              #new_if = customer_data["CustomerEdges"][cust]["provider_edges"][prov]
              
              #add the things to file
              route_data = {"ip": customerEdgeList[name], "oldInterface": existing_if, "newInterface": new_if}
              logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   Transit PE-CE(update): CE= "+ cust+" OLD PE= "+ customerProviderMapping[cust]+" NEW PE= "+prov+ " COMMAND = "+str(route_data)+"\n")
              write_yaml_data(route_data, ROUTE_FILE)
              
              r = ansible_runner.run(private_data_dir=playbook_path, playbook='changeDefaultRoute.yaml')

              #change in transit route as well
              existing_if = transitCustomerEdgeMap[customerProviderMapping[cust]]
              new_if = transitCustomerEdgeMap[prov]


              route_data = {}
              count=0

              for key, customer in enumerate(customer_data["CustomerEdges"]):
                for cr in customer:
                   if cr==cust:
                    for cn in customer[cr]["cnetwork"]:
                      route_data[count] = {}
                      route_data[count]["source"] = customer[cr]["cnetwork"][cn]
                      route_data[count]["oldInterface"] = existing_if
                      route_data[count]["newInterface"] = new_if
                      route_data[count]["netnsName"] = cr.split("ns")[0]+"_transit"
                      count+=1

              print(route_data)

              logFile.write(time.strftime("%Y%m%d-%H%M%S")+"   PE-CE(update): CE= "+ cust+" OLD PE= "+ customerProviderMapping[cust]+" NEW PE= "+prov+ " COMMAND = "+str(route_data)+"\n")
              write_yaml_data(route_data, TRANSIT_FILE)
              
              r = ansible_runner.run(private_data_dir=playbook_path, playbook='changeTransitRoute.yaml')
              
              for key, provider in enumerate(provider_data["ProviderEdges"]):
                for i in range(len(provider)):

                   if provider_data["ProviderEdges"][i]==customerProviderMapping[cust]:
                    provider_data["ProviderEdges"][i][customerProviderMapping[cust]]["customer_edges"].remove(cust)

                   if provider_data["ProviderEdges"][i]==prov:
                    provider_data["ProviderEdges"][i][prov]["customer_edges"].append(cust)




              #change in config files
              # provider_data["ProviderEdges"][customerProviderMapping[cust]]["customer_edges"].remove(cust)
              # provider_data["ProviderEdges"][prov]["customer_edges"].append(cust)
              providerLoad[prov] = (providerLoad[prov] - cLoad)
              providerLoad = dict(sorted(providerLoad.items(), key=operator.itemgetter(1), reverse = True))
              # change customerProviderMapping
              customerProviderMapping[cust] = prov
              break

  write(provider_data, "provider_edges_config.yaml")
  #save provider file
  with open(PROVIDER_EDGES_CONFIG_FILE,"r+") as f:
    f.seek(0)
    f.truncate()
    json.dump(provider_data, f)
  
  #truncate stats loader file as well
  f = open("STATS_LOADER_FILE", "w")
  f.close()

  logFile.close()


def createCEContainer(sitePrefix, PE):
 #t50ns1
  sitePrefix = sitePrefix.split("ns")
  site = "ns"+str(sitePrefix[1])
  varPE = {}
  varPE['CE'] = {}
  varPE['CE']['tenant_id'] =  sitePrefix[0][1:]
  varPE['CE']['site_id'] = sitePrefix[1]
  varPE['hypervisorType'] = "primary"
  varPE['change_container'] = 'n'
  varPE['container'] = {}
  varPE['container']['image'] = "edge_sd"
  varPE['container']['change_link'] = 'n'
  currPE = 0
  peList = []
  
  for provider in providerList:
    if provider==PE:
       currPE = int(providerList[provider])
    else:
      peList.append(int(providerList[provider]))
  
  peList.append(currPE)
  varPE['PE'] = peList
  
  ceList = {key for key in customerEdgeList.items()  
                  if key.startswith(customer.split("CE")[0])}
  currCE = 0
  
  for ce in ceList:
    
    if currCE < int(ce.split("CE")[1]):
      currCE = int(ce.split("CE")[1])

  varPE['continer']['id'] = currCE+1

  write_yaml_data(varPE,'/etc/config/container/CEConfVar.yaml')

def deleteCEContainer(sitePrefix, PE, containerId):
 #t50ns1
  sitePrefix = sitePrefix.split("ns")
  site = "ns"+str(sitePrefix[1])
  varPE = {}
  varPE['CE'] = {}
  varPE['CE']['tenant_id'] =  sitePrefix[0][1:]
  varPE['CE']['site_id'] = sitePrefix[1]
  varPE['hypervisorType'] = "primary"
  varPE['change_container'] = 'y'
  varPE['container'] = {}
  varPE['container']['image'] = "edge_sd"
  varPE['container']['id'] = 
  varPE['container']['change_link'] = 'y'
  currPE = 0
  peList = []
  
  for provider in providerList:
    if provider==PE:
       currPE = int(providerList[provider])
    else:
      peList.append(int(providerList[provider]))
  
  peList.append(currPE)
  varPE['PE'] = peList

  varPE['continer']['id'] = containerId 

  write_yaml_data(varPE,'/etc/config/container/CEConfVar.yaml')


#   ---
# CE:
#   tenant_id: 50
#   tenant_name: t50
#   site: ns2
#   site_id: 2
#   hypervisorType: primary
#   delete_container: 'y'
#   container:
#     - image: hw4
#       id: 1
#       delete_link: 'y'
#       PE: [1, 2]


def read_yaml_data(f_name):
  data = None
  with open(f_name) as stream:
    data = json.load(stream)
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
a
