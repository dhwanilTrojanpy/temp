import os
import subprocess
import re

class Webserver:
    """
    Module `Webserver` 
    Shows all running webservers on the system 
    `self.webDic={}`  Dictionary which stores all process of webservers which runs on 80 port
    `self.web1Dic={}`  Dictionary which stores all process of webservers which runs on 443 port 
    `self.webList=[]`  List that contains cluster of dictionaries
    """
    def __init__(self):
        self.webDic={}
        self.web1Dic={}
        self.webList=[]
    def display_webservers(self):
        """
        Displays webservers runs on port 80 and 443
        """
        webs=os.popen("sudo netstat -ntlp | grep 80").read().strip().splitlines()
        webs1=os.popen("sudo netstat -ntlp | grep 443").read().strip().splitlines()
        for web in webs:
            split=re.split('[\s]+',web)
            self.webDic["protcol"]=split[0]
            self.webDic["receive q"]=split[1]
            self.webDic["send q"]=split[2]
            self.webDic["local address"]=split[3]
            self.webDic["foreign address"]=split[4]
            self.webDic["state"]=split[5]
            split_ID=split[6].split("/")
            self.webDic["pid"]=split_ID[0]
            self.webDic["programme name"]=split_ID[1]
            self.webList.append(self.webDic.copy())
        for web in webs1:
            split=re.split('[\s]+',web)
            self.web1Dic["protcol"]=split[0]
            self.web1Dic["receive q"]=split[1]
            self.web1Dic["send q"]=split[2]
            self.web1Dic["local address"]=split[3]
            self.web1Dic["foreign address"]=split[4]
            self.web1Dic["state"]=split[5]
            split_ID=split[6].split("/")
            self.web1Dic["pid"]=split_ID[0]
            self.web1Dic["programme name"]=split_ID[1]
            self.webList.append(self.web1Dic.copy())
        
        return self.webList

    def handle_webserver(self,name,command):
        """
        Starts,stops and restarts given servers
        `name` name of the server
        `command` operation command
        """
        if command=="start":
           os.system("sudo systemctl start {}".format(name))
           return {"server":name,"status":"started"}
        elif command=="stop":
            os.system("sudo systemctl stop {}".format(name))
            return {"server":name,"status":"stopped"}
        elif command=="restart":
           os.system("sudo systemctl restart {}".format(name))
           return {"server":name,"status":"restarted"}      