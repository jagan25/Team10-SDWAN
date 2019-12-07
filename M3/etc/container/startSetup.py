import yaml
import sys
import os
import sys
import subprocess

LOGIC_DIR = '/logic/container/'
CONFIG_DIR = '/etc/config/container/'

def showCreate():
        try:
            option = input("\n\n1. Create transit \n2. Create Controller \n3. Create PE \n4. Create CE \n5. Create CE-PE Connection \n\n")
            if option=='1':
                #create transit file
                config_file = input("Enter the transit NS configuration file name: ")
                subprocess.call(['sudo python3 ' + LOGIC_DIR + 'transit.py create '+ CONFIG_DIR+config_file] ,shell = True)
            elif option=='2':
                #create controller file
                config_file = input("Enter the controller configuration file name: ")
                subprocess.call(['sudo python3 ' + LOGIC_DIR + 'controller.py create '+ CONFIG_DIR+config_file], shell = True)
            elif option=='3':
                #create PE file
                config_file = input("Enter the PE configuration file name: ")
                subprocess.call(['sudo python3 ' + LOGIC_DIR + 'providerEdge.py create '+ CONFIG_DIR+config_file], shell = True)
            elif option=='4':
                #create CE file
                config_file = input("Enter the CE configuration file name: ")
                subprocess.call(['sudo python3 ' + LOGIC_DIR + 'customerEdge.py create '+ CONFIG_DIR+config_file], shell = True)
            elif option=='5':
                #create CE_PE connection file
                config_file = input("Enter the CE-PE configuration file name: ")
                subprocess.call(['sudo python3 ' + LOGIC_DIR + 'customerEdge.py create '+ CONFIG_DIR+config_file], shell = True)
            else:
                print("INVALID OPTION! Please enter a valid option! \n\n")
                showCreate()
        except Exception:
            print("INVALID OPTION! Please enter a valid option! \n\n")
            showCreate()

def showDelete():
        try:
            option = input("\n\n1. Delete transit \n2. Delete Controller \n3. Delete PE \n4. Delete CE \n5. Delete CE-PE Connection \n\n")
            if option=='1':
                #delete transit
                config_file = input("Enter the transit NS configuration file name: ")
                subprocess.call(['sudo python3 ' + LOGIC_DIR + 'transit.py delete '+ CONFIG_DIR+config_file] ,shell = True)
            elif option=='2':
                #delete Controller file
                config_file = input("Enter the controller configuration file name: ")
                subprocess.call(['sudo python3  ' + LOGIC_DIR + 'controller.py delete '+ CONFIG_DIR+config_file], shell = True)
            elif option=='3':
                #delete PE file
                config_file = input("Enter the PE configuration file name: ")
                subprocess.call(['sudo python3  ' + LOGIC_DIR + 'providerEdge.py delete '+ CONFIG_DIR+config_file], shell = True)
            elif option=='4':
                #delete CE file
                config_file = input("Enter the CE configuration file name: ")
                subprocess.call(['sudo python3 ' + LOGIC_DIR + 'customerEdge.py delete '+ CONFIG_DIR+config_file], shell = True)
            elif option=='5':
                #delete CE-PE CONNECTION
                config_file = input("Enter the CE-PE configuration file name: ")
                subprocess.call(['sudo python3 ' + LOGIC_DIR + 'customerEdge.py delete '+ CONFIG_DIR+config_file], shell = True)
            else:
                print("INVALID OPTION! Please enter a valid option! \n\n")
                showDelete()
        except Exception:
            print("INVALID OPTION! Please enter a valid option! \n\n")
            showCreate()

def showConfigure():
        try:
                option= input("\n\nHave you loaded the configurations in the iptableconfig.yaml?\nPlease Enter 1 for Yes / 0 for No \n\n")
                if option=='1':
                        print("\nYour Configurations will be loaded and updated!\n")
                        #call suchu file
                elif option=='0':
                        print("\nPlease save your configurations in the iptableconfig.yaml and then execute this! \n")
                        sys.exit()
                else:
                        print("INVALID OPTION! Please enter a valid option! \n\n")
                        showConfigure()

        except Exception:
                print("INVALID OPTION! Please enter a valid option! \n\n")
                showConfigure()

def showOptions():
        try:
                option = input("1. Create (transitNS/CE/PE/Controller/CE-PE Connection) \n2. Delete (transitNS/CE/PE/Controller/CE-PE Connection) \n3. Configure IP tables \n\n")

                if option=='1':
                        showCreate()
                elif option=='2':
                        showDelete()
                elif option=='3':
                        showConfigure()
                else:
                        print("INVALID OPTION! Please enter a valid option! \n\n")
                        showOptions()
        except Exception:
                print("INVALID OPTION! Please enter a valid option! \n\n")
                showOptions()

def main():
    showOptions()


if __name__ == '__main__':
    main()

