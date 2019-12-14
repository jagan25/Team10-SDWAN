import requests
import math

pingUrl = 'http://' + sys.argv[1] + ':5000/alive'
status = {'status': 'alive'}

# @app.route('/stats', methods=['POST','GET'])
def sendStats():
    x = requests.post(pingUrl, data = status)  

if __name__ == '__main__':
    # app.run(host='0.0.0.0')
    sendStats()
