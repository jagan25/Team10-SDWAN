from flask import Flask, url_for, request
from flask import Response, make_response
import sys
import json
import requests
import datetime
from datetime import date, datetime
import os
import math
import time
import yaml

app = Flask(__name__)

def read_yaml_data(f_name):
  data = None
  with open(f_name) as stream:
    data = yaml.safe_load(stream)
  return data


def write_yaml_data(data, f_name):
  with open(f_name, 'w') as outfile:
    yaml.dump(data, outfile)

@app.route('/', methods=['POST','GET'])
def hello():
    return "Hello, Controller here!"

@app.route('/stats', methods=['POST','GET'])
def receiveStats():
     
    providerEdgeList = {}
    customerEdgeList = {}

    provider_data = read_yaml_data("provider_edges_config.yaml")
    customer_data = read_yaml_data("customer_edges_config.yaml")

    for provider in provider_data["ProviderEdges"]:
      providerEdgeList[provider_data["ProviderEdges"][provider]["ip"]] = provider
   

    for customer in customer_data["CustomerEdges"]:
      customerEdgeList[customer_data["CustomerEdges"][customer]["ip"]] = customer


    #open everytime
    f = open("statsLoader.txt", "a+")

    data = request.json
    data['ip'] = request.remote_addr
    
    name = None
    
    if data['ip'] in customerEdgeList:
      print("TRUE, IN CUSTOMER EDGE LIST")
      name = customerEdgeList[data['ip']]
      
    elif data['ip'] in providerEdgeList:
      name = providerEdgeList[data['ip']]

    if name is not None:
      f.write(name + " " + str(data['cpus']) + " " + str(data['load']) + " " + data['flag'])
      print(name + " " + str(data['cpus']) + " " + str(data['load']) + " " + data['flag'])

    f.close()
    return "NULL"

@app.route('/alive', methods=['GET','POST'])
def receiveAliveStats():
     
    providerEdgeList = {}
    customerEdgeList = {}

    provider_data = read_yaml_data("provider_edges_config.yaml")
    customer_data = read_yaml_data("customer_edges_config.yaml")

    for provider in provider_data["ProviderEdges"]:
      providerEdgeList[provider_data["ProviderEdges"][provider]["ip"]] = provider
   

    for customer in customer_data["CustomerEdges"]:
      customerEdgeList[customer_data["CustomerEdges"][customer]["ip"]] = customer
    
    #print(request.form)
    # print(request.remote_addr)
    # #open everytime
    # print(request.headers)
    # print(request)
    #data = json.loads(request.form["payload"])
    #print(data)

    name = None
    hostIP = request.remote_addr

    if hostIP in customerEdgeList:
      print("IN CUSTOMER EDGE LIST, RE")
      name = customerEdgeList[hostIP]
      
    elif hostIP in providerEdgeList:
      name = providerEdgeList[hostIP]

    if name is not None:
      
      fileData = read_yaml_data('aliveStatus.yaml')
      # with open('aliveStatus.yaml',"r+") as f:
      #   fileData = json.load(f.read())   
       
      for p in fileData['status']:
         if p['name'] == name and p['ip']== hostIP:
            p['lastPing'] = time.time()
            f.seek(0)
            f.truncate()
            json.dump(fileData, f)
            break;
      f.close()

    return "NULL"

if __name__ == '__main__':
    app.run(host='0.0.0.0')