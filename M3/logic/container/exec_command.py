import paramiko
import time

def exec_cmd(hypervisor, command, flag):
    username = 'ece792'
    if hypervisor == 'primary':
        ip, password = '192.168.122.178','Avent@2506'
    elif hypervisor == 'secondary':
        ip, password = '192.168.122.197','Avent@2504'
    handler = paramiko.SSHClient()
    handler.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    handler.connect(ip, username = username, password = password, look_for_keys = False, allow_agent = False)
    time.sleep(2)
    shell = handler.invoke_shell()
    output = shell.recv(1000)
    shell.send(command)
    time.sleep(5)
    if flag == 0:
        data = shell.recv(10000).decode('utf-8')
        data = data.split("\n")
        for line_number in range(len(data)):
            if "sudo docker inspect" in data[line_number]:
                var = data[line_number+1]
        handler.close()
        return(var)


