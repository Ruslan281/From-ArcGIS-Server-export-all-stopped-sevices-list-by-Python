# Created by Ruslan Huseynov

from collections import OrderedDict
from ConfigParser import RawConfigParser
import httplib
import urllib
import ConfigParser
from ConfigParser import RawConfigParser
import sys
import datetime
import json
import win32com.client
import os

#################################
####### CONFIG ##################
Username = 'username'         ###   # Your ArcGIS Server username 
Password = 'password'         ###   # Your ArcGIS Server password
ServerName = '10.0.0.0'       ###   # Your ArcGIS Server ip address
ServerPort = 6080             ###   # Your ArcGIS Server port number
#################################                               
#################################



class ServisSiyahi(OrderedDict):
    def __setitem__(self, key, value):
        if isinstance(value, list) and key in self:
            self[key].extend(value)
        else:
            super(OrderedDict, self).__setitem__(key, value)

config = ConfigParser.RawConfigParser()

config.read(['config.ini'])
username_1 = config.get('AboutServices', 'username')
outlook = win32com.client.Dispatch('outlook.application')
msj = outlook.CreateItem(0)

username = Username
password = Password
serverName = ServerName
serverPort = ServerPort


location = os.path.expanduser("~") + "\\" + "Desktop" + "\\"


def Token(username, password, serverName, serverPort):
    tokenURL = "/arcgis/admin/generateToken"
    params = urllib.urlencode({'username': username, 'password': password, 'client': 'requestip', 'f': 'json'})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    httpConn = httplib.HTTPConnection(serverName, serverPort)
    httpConn.request("POST", tokenURL, params, headers)
    response = httpConn.getresponse()
    if (response.status != 200):
        httpConn.close()
        return
    else:
        data = response.read()
        httpConn.close()
        token = json.loads(data)
        return token['token']


json_file = 'http://{}:6080/arcgis/rest/services?f=pjson'.format(ServerName)
url = json_file
responsee = urllib.urlopen(url)
datalar = json.loads(responsee.read())
stoppedList = []
full_url = []

for folder in datalar['folders']:

    token = Token(username, password, serverName, serverPort)

    if str(folder) == "ROOT":
        folder = ""
    else:
        folder += "/"

    folderURL = "/arcgis/admin/services/" + folder
    params = urllib.urlencode({'token': token, 'f': 'json'})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    httpConn = httplib.HTTPConnection(serverName, serverPort)
    httpConn.request("POST", folderURL, params, headers)
    response = httpConn.getresponse()
    if (response.status != 200):
        httpConn.close()
    else:
        data = response.read()
        dataObj = json.loads(data)
        httpConn.close()

        for item in dataObj['services']:
            fullSvcName = item['serviceName'] + "." + item['type']
            statusURL = "/arcgis/admin/services/" + folder + fullSvcName + "/status"
            httpConn.request("POST", statusURL, params, headers)
            statusResponse = httpConn.getresponse()
            if (statusResponse.status != 200):
                httpConn.close()

            else:
                statusData = statusResponse.read()
                statusDataObj = json.loads(statusData)
                if statusDataObj['realTimeState'] == "STOPPED":
                    stoppedList.append([fullSvcName, str(datetime.datetime.now())])

                    rest = "http://{}:6080/arcgis/rest/services".format(ServerName) + "/" + folder + fullSvcName.replace(".", "/")
                    full_url.append(rest)

            httpConn.close()
reload(sys)
sys.setdefaultencoding('utf8')
deyer=""
for i in full_url:
    deyer+=i+"\n\n<br>"

msj.To = 'rhuseynov@emlak.gov.az'
msj.Subject = '{} ArcGIS Services Status'.format(ServerName)
html_body= "<font size='4'><b>{}</b> serverinde <b><font color='red'>Stoplanan</font></b> arcgis servislerin siyahisi :</font><br><br>\n\n<b>{}</b>".format(serverName,deyer)
msj.HTMLBody = html_body
msj.Send()




