import yaml
import sys
import os 
import ansible_runner
import time

def get_config_folder_path():
  path = os.getcwd()
  path = path.split("/")
  path = path[:len(path)-2]
  return "/".join(path)

CONFIG_FOLDER_PATH = get_config_folder_path()
IP_FILE = "hostVars.yaml"
IP_ROUTE_COMMANDS_FILE = "ipRouteCommandVars.yaml"
IP_ROUTE_SCRIPT = "addIpTableRules.yaml"
PROVIDER_EDGES_CONFIG_FILE = CONFIG_FOLDER_PATH+"/config/provider_edges_config.yaml"
CUSTOMER_EDGES_CONFIG_FILE = CONFIG_FOLDER_PATH+"/config/customer_edges_config.yaml"
NETWORK_LIST_FILE = CONFIG_FOLDER_PATH+"/config/network_rule_config.yaml"
GET_IP_TABLE_RULES_SCRIPT = "get_ip_tables_rules.yaml"

LINE_NUMBER_INDEX = 0
ACTION_INDEX = 1
PROTOCOL_INDEX = 2
SOURCE_INDEX = 4
DESTINATION_INDEX = 5
COMMENT_INDEX = 7

def get_commands(nw_list):
  pass

def get_customer_edges(site, customer_data):
  customer_list = []
  for customer in customer_data["CustomerEdges"]:
      if customer.startswith(site):
        customer_list.append(customer)

  return customer_list

def get_current_ip_tables_rules(customer):
  customer_ip = customer["ip"]
  ip_data = {"host": customer_ip}
  write_yaml_data(ip_data, IP_FILE)

  r = ansible_runner.run(private_data_dir=os.getcwd(), playbook=GET_IP_TABLE_RULES_SCRIPT)
  out = r.get_fact_cache(customer_ip)
  rules = str(out["output"]).split("Chain ")
  rules = rules[1]
  rule_array = rules.split("\n")

  new_rule_array = []
  for row in rule_array:
    ip = " ".join(row.split())
    if ip != '':
      new_rule_array.append(ip)

  new_rule_array.pop(0)
  new_rule_array.pop(0)

  return new_rule_array

def find_conflicting_rules(current_rules, rule):
  for current_rule in current_rules:
    c_rule = current_rule.split(" ")
    temp_source = "anywhere"
    if "SOURCE" in rule:
      temp_source = rule["SOURCE"]
    temp_destination = "anywhere"
    if "DESTINATION" in rule:
      temp_destination = rule["DESTINATION"]
    if temp_source == "0.0.0.0/0":
      temp_source = "anywhere"
    if temp_destination == "0.0.0.0/0":
      temp_destination = "anywhere"
    if c_rule[SOURCE_INDEX] == temp_source and c_rule[DESTINATION_INDEX] == temp_destination:
      if rule["PROTOCOL"] == "SSH":
        if c_rule[COMMENT_INDEX].contains(rule["PROTOCOL"]):
          if c_rule[ACTION_INDEX] != rule["ACTION"]:
            return int(c_rule[LINE_NUMBER_INDEX])
          else:
            return False
      else:
        if c_rule[PROTOCOL_INDEX] == rule["PROTOCOL"]:
          if c_rule[ACTION_INDEX] != rule["ACTION"]:
            return int(c_rule[LINE_NUMBER_INDEX])
          else:
            return False
  return True

def construct_rule(rule):
  s = "iptables -I INPUT 1 -p " + rule["PROTOCOL"]
  if "SOURCE" in rule:
    s += " -s " + rule["SOURCE"]
  if "DESTINATION" in rule:
    s += " -d " + rule["DESTINATION"]

  s += " -j " + rule["ACTION"] 
  return s

def get_delete_rules(line_nums):
  delete_rules = []
  for i, num in enumerate(line_nums):
    delete_rules.append("iptables -D INPUT " + str(line_nums[i]-i))

  return delete_rules

def run_ansible_script():
  provider_data = read_yaml_data(PROVIDER_EDGES_CONFIG_FILE)
  customer_data = read_yaml_data(CUSTOMER_EDGES_CONFIG_FILE)
  network_data = read_yaml_data(NETWORK_LIST_FILE)

  command_list = []

  for site in network_data:
    customer_edges_list = get_customer_edges(site, customer_data)
    conflicitng_rules_line_numbers = []
    new_rules = []
    if len(customer_edges_list) > 0:
      current_ip_table_rules = get_current_ip_tables_rules(customer_data["CustomerEdges"][customer_edges_list[0]])
      for rule in network_data[site]:
        res = find_conflicting_rules(current_ip_table_rules, rule)

        if type(res) is int:
          conflicitng_rules_line_numbers.append(res)
        elif res == True:
          new_rules.append(construct_rule(rule))

    delete_rules = get_delete_rules(conflicitng_rules_line_numbers)
    new_rules = delete_rules + new_rules
    cmd_data = {"IPTableCommands": new_rules}
    write_yaml_data(cmd_data, IP_ROUTE_COMMANDS_FILE)
    for customer in customer_edges_list:
      for rule in new_rules:
        l = time.strftime("%Y%m%d-%H%M%S") + "CE IPTABLE UPDATE: " + customer + "COMMAND: " + rule + "\n"
        logFile.write(l)

      customer_ip = customer_data["CustomerEdges"][customer]["ip"]
      ip_data = {"host": customer_ip}
      write_yaml_data(ip_data, IP_FILE)

      r = ansible_runner.run(private_data_dir=os.getcwd(), playbook=IP_ROUTE_SCRIPT)
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
  fileName = "/tmp/logs/log_"+time.strftime("%Y%m%d")+".txt"
  logFile = open(fileName, 'a+')
  run_ansible_script()
  logFile.close()

if __name__ == '__main__':
    main()
