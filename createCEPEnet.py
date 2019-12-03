import sys
import yaml
import subprocess
import time

def main():

    fileName = "/var/log/log_"+time.strftime("%Y%m%d")+".txt"
    logFile = open(fileName, 'a+')
    if(len(sys.argv)<2):
        print("\nERROR: less than 2 arguments given!!! Require 2 arguments to run")
        logFile.write(time.strftime("%Y%m%d-%H%M%S")+"  ERROR: less than 2 arguments given!!! Require 2 arguments to run :"+ str(sys.argv)+"\n")
        exit(0)
    else:
        yFileName = sys.argv[2]
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
                        if str(sys.argv[1]).lower() == "create":
                            print("Running Ansible playbook to create and start bridges and network")
                            subprocess.call(['sudo ansible-playbook createCEPEnet.yaml -e network=' + net + ' -e bridge=' + bridge + ' -vvvvv'], shell=True)
                            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"  Running Ansible playbook to create and start bridges and network :"+ "sudo ansible-playbook createCEPEnet.yaml -e network=" +net+" -e bridge=" + bridge + " -vvvvv"+"\n")
                            print("Attach interface bridge -- CE")
                            subprocess.call(['sudo virsh attach-interface --domain ' + str(yFile['siteNS']) + str(c) + ' --type network ' + net + ' --model virtio --config --live'],shell=True)
                            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"  Attach interface bridge -- CE :"+ 'sudo virsh attach-interface --domain ' + str(yFile['siteNS']) + str(c) + ' --type network ' + net + ' --model virtio --config --live'+"\n")

                            print("Attach interface bridge -- PE")
                            subprocess.call(['sudo virsh attach-interface --domain ' + str(yFile['tenantName']) + "_" + str(p) + ' --type network ' + net + ' --model virtio --config --live'],shell=True)
                            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"  Attach interface bridge -- PE :"+ 'sudo virsh attach-interface --domain ' + str(yFile['tenantName']) + "_" + str(p) + ' --type network ' + net + ' --model virtio --config --live'+"\n")
                        elif str(sys.argv[1]).lower() == "delete":
                            print("Running Ansible playbook to delete bridges and network")
                            subprocess.call(['sudo bash deleteNet.sh '+net+' '+bridge], shell=True)
                            logFile.write(time.strftime("%Y%m%d-%H%M%S")+"  Running Ansible playbook to delete bridges and network :"+ 'sudo deleteNet.sh '+net+' '+bridge+"\n")
                            exit(0)                                        
                        else:
                            logging.error("\nERROR: Unrecognized Command!!!")
                            logFile.write(time.strftime("%Y%m%d-%H%M%S")+" ERROR: Unrecognized Command!!! "+ str(sys.argv)+ "\n")
                            exit(0)

            except Exception as e:
                print(e)
                logFile.write(time.strftime("%Y%m%d-%H%M%S")+" Exception "+ str(e)+ "\n")
    logFile.close()

if __name__ == '__main__':
    main()
