import yaml
import sys
import os 
import ansible_runner
import time

CONFIG_FOLDER_PATH = '/etc/config/container/'
ANSIBLE_FOLDER_PATH = '/var/scripts/container/'
IP_FILE = ANSIBLE_FOLDER_PATH+"hostVars.yaml"
IP_ROUTE_COMMANDS_FILE = ANSIBLE_FOLDER_PATH+"ipRouteCommandVars.yaml"
IP_ROUTE_SCRIPT = ANSIBLE_FOLDER_PATH+"addIpTableRules.yaml"
PROVIDER_EDGES_CONFIG_FILE = CONFIG_FOLDER_PATH+"PEConfig.txt"
CUSTOMER_EDGES_CONFIG_FILE = CONFIG_FOLDER_PATH+"CEConfig.txt"
ALLOWED_NETWORK_LIST_FILE = CONFIG_FOLDER_PATH+"allowed_network_list.yaml"

def run_ansible_script(logFile):
  provider_data = read_txt_data(PROVIDER_EDGES_CONFIG_FILE)
  customer_data = read_txt_data(CUSTOMER_EDGES_CONFIG_FILE)
  network_data = read_yaml_data(ALLOWED_NETWORK_LIST_FILE)

  command_list = ["iptables -A INPUT -p icmp -m limit --limit 1/s --limit-burst 1 -j ACCEPT",
                  "iptables -A INPUT -p icmp -m limit --limit 1/s --limit-burst 1 -j LOG --log-prefix PING-DROP",
                  "iptables -A INPUT -p icmp -j DROP"]

  for nw in network_data["AllowedNetworks"]:
    allow_nw_cmd = "iptables -A INPUT -s "+nw+" -j ACCEPT"
    command_list.append(allow_nw_cmd)

  cmd_data = {"IPTableCommands": command_list}
  write_yaml_data(cmd_data, IP_ROUTE_COMMANDS_FILE)
  print(cmd_data)

  Writing to log file
  for cmd in command_list:
    for key, provider in enumerate(provider_data["ProviderEdges"]):
      for pr in provider:
        providerEdgeList[provider[pr]["ip"]] = pr
        l = time.strftime("%Y%m%d-%H%M%S") + "PE IPTABLE UPDATE: " + pr + "COMMAND: " + cmd + "\n"
        logFile.write(l)
    for key, customer in enumerate(customer_data["CustomerEdges"]):
      for cr in customer:
        customerEdgeList[customer[cr]["ip"]] = cr
        l = time.strftime("%Y%m%d-%H%M%S") + "CE IPTABLE UPDATE: " + cr + "COMMAND: " + cmd + "\n"
        logFile.write(l)

  
  for key, provider in enumerate(provider_data["ProviderEdges"]):
    for pr in provider:
      provider_ip = provider[pr]["ip"]
      ip_data = {"host": provider_ip}
      write_yaml_data(ip_data, IP_FILE)
      
      r = ansible_runner.run(private_data_dir=ANSIBLE_FOLDER_PATH, playbook=IP_ROUTE_SCRIPT)
      out = r.get_fact_cache(provider_ip)

  for key, customer in enumerate(customer_data["CustomerEdges"]):
    for cr in customer:
      customer_ip = customer[cr]["ip"]
      ip_data = {"host": customer_ip}
      write_yaml_data(ip_data, IP_FILE)

      r = ansible_runner.run(private_data_dir=ANSIBLE_FOLDER_PATH, playbook=IP_ROUTE_SCRIPT)
      out = r.get_fact_cache(customer_ip)

def read_yaml_data(f_name):
  data = None
  with open(f_name) as stream:
    data = yaml.safe_load(stream)
  return data

def write_yaml_data(data, f_name):
  with open(f_name, 'w') as outfile:
    yaml.dump(data, outfile)

def read_txt_data(f_name):
  data = None
  with open(f_name) as stream:
    data = json.load(stream)
  return data

def main():
  fileName = "/var/log/log_"+time.strftime("%Y%m%d")+".txt"
  logFile = open(fileName, 'a+')
  
  run_ansible_script(logFile)

  logFile.close()


if __name__ == '__main__':
    main()

