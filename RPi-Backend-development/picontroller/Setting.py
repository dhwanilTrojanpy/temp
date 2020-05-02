import os
import subprocess
import re
# import bluetooth
class Setting:
    # def __init__(self):
    #     os.system("sudo apt-get install network-manager")
                
    def installed_app(self):
        pkgDic={}
        pkgList=[]
        appDic={}
        appList=[]
        pkgs=os.popen('./app.sh').read().splitlines()
        pkgDic["application"]=pkgs
        pkgList.append(pkgDic.copy())
        return pkgList
        apps=os.popen('snap list').read().strip().splitlines()[1:]
        for app in apps:
            split=app.split(" ")
            appDic["application"]=split[0]
            appList.append(appDic.copy())
        return appList    
    

    def update(self):
        updateDic={}
        updateList=[]
        ups=os.popen('sudo apt-get update').read().strip().splitlines()
        updateDic["status"]=ups
        updateList.append(updateDic.copy())
        return updateList

    def system_operation(self,command):
        if command=="shutdown":
            os.system("sudo /sbin/shutdown -h now")
            return True
        elif command=="restart":
            os.system("sudo /sbin/reboot")
            return True
        elif command=="hibernate":
            os.system("sudo /sbin/pm-hibernate")
            return True

    def active_connection(self):
        deviceDic={}
        deviceList=[] 
        devices=os.popen("nmcli d").read().strip().splitlines()[1:]
        for device in devices:
            split=re.split("[\s]+",device)
            deviceDic["device"]=split[0]
            deviceDic["type"]=split[1]
            deviceDic["state"]=split[2]
            if "" in split[3:]:
                deviceDic["connection"]=split[3:-1]
            deviceList.append(deviceDic.copy())
        return deviceList 

    def connect_ethernet(self,command,eth_name):
        if command == "connect":
            os.system("sudo ip link set up {}".format(eth_name))
            return {"status":"Connecting"}
        elif command == "disconnect":    
            os.system("sudo ip link set down {}".format(eth_name))
            return {"status":"Disconnecting"}

    def printer(self,command,printer_name,file_path_with_name):
        if command=="list":
            cmdsList=[]
            cmdsDic={}
            cmds=os.popen("sudo lpstat -s").read().strip().splitlines()
            cmdsDic["printer"]=cmds
            cmdsList.append(cmdsDic.copy())
            return cmdsList

        elif command=="print":        
            os.system("lp -d {} {}".format(printer_name,file_path_with_name))
            return {"message":"Printing"}
            

    def bluetooth_devices(self):
        nearby_devices = bluetooth.discover_devices(lookup_names=True)
        print("Total - {}".format(len(nearby_devices)))

        for addr, name in nearby_devices:
            try:       
                return {"Address":"{}".format(addr),"Name":"{}".format(name)} 
            except UnicodeEncodeError:    
                return {"Address":"{}".format(addr),"Name":"{}".format(name.encode("utf-8","replace"))}
                
    def bluetooth_operations(self,command,mac_address=None):
        if command == "start":
            os.system("sudo systemsctl start bluetooth.service")
        elif command == "stop":    
            os.system("sudo systemsctl stop bluetooth.service")
        elif command =="status":
            os.system("sudo systemsctl status bluetooth.service")
        elif command =="check":
            os.system("sudo systemctl is-enabled bluetooth.services")
        elif command == "connect":
            os.system("bt-audio -c {}".format(mac_address))        

    def authchecker(self,username,password):
        FAIL = b'Password: \r\nsu: Authentication failure'
        msg = "No passwd entry for user '%s'" % username
        INVALID = msg.encode('utf-8')
        msg_user = "su: user %s does not exist" % username
        INVALID_user = msg_user.encode('utf-8')
        ret = 0
        try:
            cmd = '{ sleep 0.1; echo "%s"; } | script -q -c "su -l %s -c ls /root" /dev/null' % (password,username) 
            ret = subprocess.check_output(cmd, shell=True).strip()
            if FAIL == ret or INVALID == ret or INVALID_user == ret:
                return "Invalid username or password"
            else:
                return "Valid password"
        except Exception as e:
            return e