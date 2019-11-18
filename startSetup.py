import yaml
import sys
import os 
import sys

def showCreate():
	try:
		option = input("\n\n1. Create CE \n2. Create PE \n3. Create Controller \n4. Create CE-PE Connection \n\n")
		if option==1:
			#create ce file
			print("blah")
		elif option==2:
			#create PE file
			print("blah")
		elif option==3:	
			#create controller file
			print("blah")
		elif option==4:
			#create CE_PE connection file
			print("blah")	
		else:
			print("INVALID OPTION! Please enter a valid option! \n\n")
			showCreate()
	except Exception:
		print("INVALID OPTION! Please enter a valid option! \n\n")
		showCreate()

def showDelete():
	try:
		option = input("\n\n1. Delete CE \n2. Delete PE \n3. Delete Controller \n4. Delete CE-PE Connection \n\n")
		if option==1:
			#delete ce file
			print("blah")
		elif option==2:
			#delete PE file
			print("blah")
		elif option==3:	
			#delete controller file
			print("blah")
		elif option==4:
			#delete CE_PE connection file
			print("blah")	
		else:
			print("INVALID OPTION! Please enter a valid option! \n\n")
			showDelete()
	except Exception:
		print("INVALID OPTION! Please enter a valid option! \n\n")
		showCreate()

def showConfigure():
	try:
		option= input("\n\nHave you loaded the configurations in the iptableconfig.yaml?\nPlease Enter 1 for Yes / 0 for No \n\n")
		if option==1:
			print("\nYour Configurations will be loaded and updated!\n")
			#call suchu file
		elif option==0:
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
		option = input("1. Create (CE/PE/Controller/CE-PE Connection) \n2. Delete (CE/PE/Controller/CE-PE Connection) \n3. Configure IP tables \n\n")
		
		if option==1:
			showCreate()
		elif option==2:
			showDelete()
		elif option==3:	
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
