import os
import re
import json
class Service:
    """
    Module `Services`
    Module which display all services present in current system
    User can start and stop services accordingly.
    `self.dic` Dictionary which stores name and status of all services
    `self.li` List that contains cluster of dictionaries
    `self.cmds` Displays all services 
    """
    def __init__(self):
        self.dic={}
        self.li=[]
        self.cmds=os.popen("service --status-all").read().strip().splitlines()
    def check_services(self):
        """
        To check services present in the current system
        """
        count=0
        for cmd in self.cmds:
            split = re.split('[\s]+',cmd)
            count=count+1
            self.dic["no"]=count
            if split[0] =="":
                if split[2]=="+":
                    self.dic["status"]="running"
                if split[2]=="-":
                    self.dic["status"]="stopped"
                self.dic["service"]=split[4] 
            else:
                if split[1]=="+":
                    self.dic["status"]="running"
                if split[1]=="-":
                    self.dic["status"]="stopped"
                self.dic["service"]=split[3] 
                self.dic["action"]="button"
            self.li.append(self.dic.copy())
        return self.li

    def service_after(self,service_name):
        services=os.popen("systemctl list-dependencies {}".format(service_name)).read().strip().splitlines()[1:]
        for Service in services:
            return Service[4:]

    def service_before(self,service_name):
        services=os.popen("systemctl list-dependencies --reverse {}".format(service_name)).read().strip().splitlines()[1:]
        for Service in services:
            return Service[4:]

    def service_path(self,service_name):
        services=os.popen("locate {} | grep systemd".format(service_name)).read().strip().splitlines()[0]
        return services 

    def service_status(self,service_name):    
        services=os.popen("systemctl status {}".format(service_name)).read().strip().splitlines()[1:3]
        return services 

    def service_details(self,service_name):
        serDic={}
        serList=[]
        serDic["status"]=service_status(service_name)
        serDic["path"]=service_path(service_name)
        serDic["after"]=service_after(service_name)
        serDic["before"]=service_before(service_name)
        serList.append(serDic.copy())
        return serList

    def handle_service(self,command,service_name):
        """
        for starting and stoping services
        """      
        if command=="1": 
            os.system("sudo systemctl start {}".format(service_name))
            return True
        elif command=="2":    
            os.system("sudo systemctl stop {}".format(service_name))
            return True
        elif command=="3":   
            os.system("sudo systemctl restart {}".format(service_name))
            return True

                
              