import os
import subprocess
import re

class Ports:
    """
    Module `Port` 
    Shows all running port on the system 
    `self.portDic={}`  Dictionary which stores all process 
    `self.portList=[]`  List that contains cluster of dictionaries
    """
    def __init__(self):
        self.portDic={}
        self.portList=[]
    def display_port(self):
        """
        Displays all process along with Ports and Process IDS
        """
        ports=os.popen("sudo netstat -ntlp").read().strip().splitlines()[2:]
        for port in ports:
            split=re.split('[\s]+',port)
            self.portDic["Protcol"]=split[0]
            self.portDic["Receive Q"]=split[1]
            self.portDic["Send Q"]=split[2]
            split_port=split[3].split(":")
            if split_port[1]=="":
                self.portDic["port"]="No Port"    
            else:
                self.portDic["port"]=split_port[1]
            self.portDic["Foreign Address"]=split[4]
            self.portDic["State"]=split[5]
            split_ID=split[6].split("/")
            self.portDic["PID"]=split_ID[0]
            self.portDic["Programme Name"]=split_ID[1]
            self.portDic["action"]="btn"
            self.portList.append(self.portDic.copy())
        return self.portList    

    def kill_process(self,PID):
        """
        Kill Process with given process ID
        `PID` Process ID 
        """
        os.system("sudo kill {}".format(PID))
        return True    
           
