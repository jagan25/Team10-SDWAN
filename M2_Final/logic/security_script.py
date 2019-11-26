import yaml
import sys
import os 
import ansible_runner
import time

CONFIG_FOLDER_PATH = '/etc/config/'
ANSIBLE_FOLDER_PATH = '/var/scripts/'
IP_FILE = ANSIBLE_FOLDER_PATH+"hostVars.yaml"
IP_ROUTE_COMMANDS_FILE = ANSIBLE_FOLDER_PATH+"ipRouteCommandVars.yaml"
IP_ROUTE_SCRIPT = "addIpTableRules.yaml"
PROVIDER_EDGES_CONFIG_FILE = CONFIG_FOLDER_PATH+"provider_edges_config.yaml"
CUSTOMER_EDGES_CONFIG_FILE = CONFIG_FOLDER_PATH+"customer_edges_config.yaml"
ALLOWED_NETWORK_LIST_FILE = CONFIG_FOLDER_PATH+"allowed_network_list.yaml"

fileName = "/var/log/log_"+time.strftime("%Y%m%d")+".txt"
logFile = open(fileName, 'a+')

def run_ansible_script():
  provider_data = read_yaml_data(PROVIDER_EDGES_CONFIG_FILE)
  customer_data = read_yaml_data(CUSTOMER_EDGES_CONFIG_FILE)
  network_data = read_yaml_data(ALLOWED_NETWORK_LIST_FILE)

  command_list = ["iptables -A INPUT -p icmp -m limit --limit 1/s --limit-burst 1 -j ACCEPT",
                  "iptables -A INPUT -p icmp -m limit --limit 1/s --limit-burst 1 -j LOG --log-prefix PING-DROP",
                  "iptables -A INPUT -p icmp -j DROP"]

  for nw in network_data["AllowedNetworks"]:
    allow_nw_cmd = "iptables -A INPUT -s "+nw+" -j ACCEPT"
    command_list.append(allow_nw_cmd)

  deny_all_cmd = "iptables -A INPUT -s 0.0.0.0/0 -j DROP"
  command_list.append(deny_all_cmd)
  cmd_data = {"IPTableCommands": command_list}
  write_yaml_data(cmd_data, IP_ROUTE_COMMANDS_FILE)

  # Writing to log file
  for cmd in command_list:
    for provider_name in provider_data["ProviderEdges"]:
      l = time.strftime("%Y%m%d-%H%M%S") + "PE IPTABLE UPDATE: " + provider_name + "COMMAND: " + cmd + "\n"
      logFile.write(l)
    for customer_name in customer_data["CustomerEdges"]:
      l = time.strftime("%Y%m%d-%H%M%S") + "CE IPTABLE UPDATE: " + customer_name + "COMMAND: " + cmd + "\n"
      logFile.write(l)


  # for provider_name in provider_data["ProviderEdges"]:
  #   provider_ip = provider_data["ProviderEdges"][provider_name]["ip"]
  #   ip_data = {"host": provider_ip}
  #   write_yaml_data(ip_data, IP_FILE)

  #   r = ansible_runner.run(private_data_dir=ANSIBLE_FOLDER_PATH, playbook=IP_ROUTE_SCRIPT)
  #   out = r.get_fact_cache(provider_ip)

  for customer_name in customer_data["CustomerEdges"]:
    customer_ip = customer_data["CustomerEdges"][customer_name]["ip"]
    ip_data = {"host": customer_ip}
    write_yaml_data(ip_data, IP_FILE)

    print(command_list)

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


def main():
  run_ansible_script()
  logFile.close()


if __name__ == '__main__':
    main()
