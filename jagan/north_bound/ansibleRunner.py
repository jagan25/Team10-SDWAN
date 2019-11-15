import yaml
import sys
import os 
import json
import ansible_runner
playbook_path = os.getcwd()
playbook_path = playbook_path.replace("north_bound", "ansible_scripts")

def run_ansible_script(script_name, ip_file):

  # Refer https://ansible-runner.readthedocs.io/en/latest/python_interface.html for ansible doc

  r = ansible_runner.run(private_data_dir=playbook_path, playbook='routerConnectionCreation.yaml')


def read_yaml_data(f_name):
  
  data = None
  with open(f_name) as stream:
    data = yaml.safe_load(stream)
  return data


def write_yaml_data(data, f_name):
  
  with open(f_name, 'w') as outfile:
    yaml.dump(data, outfile)

def write_to_json(data):
  
  with open(playbook_path+'/rtor.json', 'w') as outfile:
    json.dump(data, outfile)

def createVPC(file):
  data = read_yaml_data(file)
  data = data['routers']
  print(data)
  for i in range(len(data)):
    write_to_json(data[i])
    run_ansible_script("dummy", "dummy")

    
 # print(data)
  #vpc_data = read_yaml_data(VPC_FILE)

  #valid = validateInput(data, vpc_data)


def main():
  file = sys.argv[1]
  createVPC(file)
 

if __name__ == '__main__':
    main()


# createVPC(file)
# run_ansible_script("dummy", "dummy")
