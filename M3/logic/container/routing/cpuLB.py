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


# See if PE has to be changed
# If PE is changed, then think about CE
# IF PE is not changed, think only about auto scaling

# this is because CE and PE can have different configurations

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
  customerEdgeCount = {}
  providerIdList = {}


  for provider in provider_data["ProviderEdges"]:
      providerList[provider] = provider_data["ProviderEdges"][provider]["ip"]
      providerIdList[provider] = provider_data["ProviderEdges"][provider]["id"]

      if(len(provider_data["ProviderEdges"][provider]["customer_edges"]))>0:
        for i in provider_data["ProviderEdges"][provider]["customer_edges"]:
          customerProviderMapping[i] = provider
      

  for customer in customer_data["CustomerEdges"]:
      customerEdgeList[customer] = customer_data["CustomerEdges"][customer]["ip"]

  for customer in customer_data["CECount"]:
      customerEdgeCount[customer] = {}
      customerEdgeCount[customer]['max'] = customer_data["CECount"][customer]['max']
      customerEdgeCount[customer]['min'] = customer_data["CECount"][customer]['min']


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
  for customer in customerVM




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



            sudo python customerEdge.py create CEConfVar.yaml

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
  write_yaml_data(customer_data, "customer_edges_config.yaml")
  logFile.close()


def createCEContainer(sitePrefix, PE, CENumber):
 #t50ns1
  sitePrefix = sitePrefix.split("ns")
  site = "ns"+str(sitePrefix[1])
  varPE = {}
  varPE['CE'] = {}
  varPE['CE']['tenant_id'] =  sitePrefix[0][1:]
  varPE['CE']['site_id'] = sitePrefix[1]
  varPE['hypervisorType'] = "primary"
  varPE['delete_container'] = 'n'
  varPE['container'] = {}
  varPE['container']['image'] = "hw4"
  varPE['container']['id'] = 
  varPE['container']['delete_link'] = 'n'
  currPE = 0
  peList = []
  
  for provider in providerIdList:
    if provider==PE:
       currPE = int(providerIdList[provider])
    else:
      peList.append(int(providerIdList[provider]))
  
  peList.append(currPE)
  varPE['PE'] = peList
  
  ceList = {key for key in customerEdgeList.items()  
                  if key.startswith(customer.split("CE")[0])}
  currCE = 0
  
  for ce in ceList:
    
    if currCE < int(ce.split("CE")[1]):
      currCE = int(ce.split("CE")[1])

  varPE['continer']['id'] = currCE  



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
