SDWAN-as-a-Service

The northbound consist of user input YAML files and startsetup.py script which creates/deletes the network infrastructure as per user configuration.

The user has to execute the following files in the following order:
1. create transit
2. create controller
3. create provider edge routers
4. create customer edge routers

We also provide the functionality to user to create a site with our solution:
1. create site
2. create customer edge router

To run the setup:
python startSetup.py
