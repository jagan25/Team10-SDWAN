import sys
import yaml
import subprocess

if(len(sys.argv)<1):
    print("\nERROR: No arguments given")
    exit(0)
else:
    yFileName = sys.argv[1]
    # check if yaml file is passed
    if yFileName.endswith(".yml") or yFileName.endswith(".yaml"):
        try:
            with open(yFileName,"r") as file:
                yFile = yaml.load(file)
            ce = yFile['CE']
            pe = yFile['PE']
            siteID = yFile['siteID']
            for c in ce:
                for p in pe:
                    net = str(siteID) + str(c) + str(p) +'Net'
                    bridge = str(siteID) + str(c) + str(p) +'br'
                    print("Running Ansible playbook to create and start bridges and network")
                    subprocess.call(['sudo ansible-playbook createCEPEnet.yaml -e network=' + net + ' -e bridge=' + bridge + ' -vvvvv'], shell=True)
                    print("Attach interface bridge -- CE")
                    subprocess.call(['sudo virsh attach-interface --domain ' + str(yFile['siteNS']) + str(
                        c) + ' --type network ' + net + ' --model virtio --config --live'],
                               shell=True)
                    print("Attach interface bridge -- PE")
                    subprocess.call(['sudo virsh attach-interface --domain ' + str(yFile['tenantName']) + "_" + str(
                        p) + ' --type network ' + net + ' --model virtio --config --live'],
                               shell=True)
        except Exception as e:
            print(e)
