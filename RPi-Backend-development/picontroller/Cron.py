import os
import subprocess
import re

class Cron:
    
    def install_cron(self):
        resDic={}
        resList=[]
        results=os.popen("dpkg -l cron").read().strip().splitlines()[5:]
        for result in results:
            split=re.split("[\s]+",result)
        if split[0]=="un":
            os.system("sudo apt install cron")
        
        results=os.popen("dpkg -l cron").read().strip().splitlines()[5:]
        for result in results:
                split=re.split("[\s]+",result)
                resDic["status"]=split[0]
                resDic["name"]=split[1]
                resDic["version"]=split[2]
                resDic["architechture"]=split[3]
                resList.append(resDic.copy())
        print(resList)

    def cron_status(self):
        staDic={}
        staList=[]
        status=os.popen("systemctl status cron").read().strip().splitlines()[2:3]
        for sts in status:
            split=re.split("[\s]+",sts)
            staDic["status"]=split[2]+split[3]    
            staList.append(staDic.copy())
        print(staList) 

    def cron_operation(self,command):
        if command=="start":
            os.system("systemctl start cron")
            return {"status":"Cron has been started"}
        elif command=="stop":
            os.system("systemctl stop cron")
            return {"status":"Cron has been stopped"}    
        elif command=="list":
            listDic={}
            listList=[]
            cmds=os.popen("crontab -l").read().strip().splitlines()
            listDic["crons"]=cmds
            listList.append(listDic.copy())
            print(listList)
        elif command=="remove":
            listDic={}
            listList=[]
            cmds=os.popen("crontab -r").read().strip().splitlines()
            listDic["crons"]=cmds
            listList.append(listDic.copy())
            print(listList)
        

    def set_crontab(self,cron_name,exec_cmd,minute,hour,day,month,weekday):
        os.system("crontab -l > {}".format(cron_name))
        os.system('echo "{} {} {} {} {} {} ">> {}'.format(minute,hour,day,month,weekday,exec_cmd,cron_name))
        os.system("crontab {}".format(cron_name))
        os.system("rm {}".format(cron_name))
