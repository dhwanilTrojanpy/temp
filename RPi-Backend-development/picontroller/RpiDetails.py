from subprocess import check_output
import subprocess
import os
import re
import psutil

class Details(object):
    
    def __init__(self,logger=None):
        self.details = {}
        self.log = logger

    def Username(self):
        username = os.popen("who | awk '{print $1}'").read().strip().splitlines()[0]
        self.details['username']= username
        return username

    def Hostname(self):
        hostname = check_output(['cat','/proc/sys/kernel/hostname']).strip().decode('UTF-8')
        self.details['hostname']= hostname
        return self.details 

    def Ip(self):
        ip = check_output(['hostname','-I']).strip().decode('UTF-8')
        self.details['ip']= ip
        return self.details 
    
    def CpuTemp(self):
        temp = check_output(['/opt/vc/bin/vcgencmd','measure_temp']).strip().decode('UTF-8').replace("temp=","")
        self.details['temp']= temp
        return temp
    
    def CpuClock(self):
        clk = check_output(['cat','/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq']).strip().decode('UTF-8')
        self.details['clk']= {}
        self.details['clk']['minclk'] = self.CpuMinClock()
        self.details['clk']['maxclk'] = self.CpuMaxClock() 
        return round(int(clk)/1000)
    
    def CpuMinClock(self):
        minclk = check_output(['cat','/sys/devices/system/cpu/cpu0/cpufreq/scaling_min_freq']).strip().decode('UTF-8')
        return round(int(minclk)/1000)
    
    def CpuMaxClock(self):
        maxclk = check_output(['cat','/sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq']).strip().decode('UTF-8')
        return round(int(maxclk)/1000)
    
    def CpuType(self):
        type = check_output(['cat','/proc/cpuinfo']).strip().decode('UTF-8').replace("\t","")
        hardware = type.split("Hardware:",1)[1].split("\n",1)[0].strip()
        self.details['cputype'] = hardware
        return hardware
    
    def CpuModel(self):
        type = check_output(['cat','/proc/cpuinfo']).strip().decode('UTF-8').replace("\t","")
        modelname = type.split("model name:",1)[1].split("\n",1)[0].strip()
        return modelname
    
    def CpuLoadAvg(self):
        loadavg = check_output(['cat','/proc/loadavg']).strip().decode('UTF-8')
        timeavg = list(loadavg.split(" "))
        load = []  
        min_1 = round(float(timeavg[0])*100)
        load.append(min_1)
        min_5 = round(float(timeavg[1])*100)
        load.append(min_5)
        min_15 = round(float(timeavg[2])*100)
        load.append(min_15)  
        return load
    
    def cpuUsage(self):
        cpu_percent=psutil.cpu_percent()
        return cpu_percent
    
    def Distribution(self):
        dist = os.popen('cat /etc/issue | cut -d " " -f 1-3').read().strip()             
        return dist
    
    def KernelVersion(self):
        kernel= os.popen('cat /proc/version | cut -d " " -f 1,3').read().strip()
        return kernel
    
    def CountRunningTask(self):
        runningtask = os.popen('ps -auxeaf| wc -l').read().strip()
        return runningtask
    
    def CountInstalledPackages(self):
        countpackages = os.popen('dpkg --get-selections | grep -v deinstall | wc -l').read().strip()
        return countpackages
    
    def InstalledPackages(self):
        packages = list(os.popen('dpkg -l | grep ^ii').read().strip().split("\n"))
        installpackages = list(map(lambda package:re.split("\s+", package,4), packages))
        return installpackages
    
    def Revision(self):
        revision = {
            2:{'revision' : '0002', 'model' : 'B', 'pcb' : '1.0', 'memory' : 256, 'manufacturer' : ''},
            3:{'revision' : '0003', 'model' : 'B', 'pcb' : '1.0', 'memory' : 256, 'manufacturer' : ''},
            4:{'revision' : '0004', 'model' : 'B', 'pcb' : '2.0', 'memory' : 256, 'manufacturer' : 'Sony'},
            5:{'revision' : '0005', 'model' : 'B', 'pcb' : '2.0', 'memory' : 256, 'manufacturer' : 'Qisda'},
            6:{'revision' : '0006', 'model' : 'B', 'pcb' : '2.0', 'memory' : 256, 'manufacturer' : 'Egoman'},
            7:{'revision' : '0007', 'model' : 'A', 'pcb' : '2.0', 'memory' : 256, 'manufacturer' : 'Egoman'},
            8:{'revision' : '0008', 'model' : 'A', 'pcb' : '2.0', 'memory' : 256, 'manufacturer' : 'Sony'},
            9:{'revision' : '0009', 'model' : 'A', 'pcb' : '2.0', 'memory' : 256, 'manufacturer' : 'Qisda'},
            13:{'revision' : '000d', 'model' : 'B', 'pcb' : '2.0', 'memory' : 512, 'manufacturer' : 'Egoman'},
            14:{'revision' : '000e', 'model' : 'B', 'pcb' : '2.0', 'memory' : 512, 'manufacturer' : 'Sony'},
            15:{'revision' : '000f', 'model' : 'B', 'pcb' : '2.0', 'memory' : 512, 'manufacturer' : 'Qisda'},
            16:{'revision' : '0010', 'model' : 'B+', 'pcb' : '1.0', 'memory' : 512, 'manufacturer' : 'ony'},
            17:{'revision' : '0011', 'model' : 'Compute Module', 'pcb' : '1.0', 'memory' : 512, 'manufacturer' : 'Sony'},
            18:{'revision' : '0012', 'model' : 'A+', 'pcb' : '1.0', 'memory' : 256, 'manufacturer' : 'Sony'},
            19:{'revision' : '0013', 'model' : 'B+', 'pcb' : '1.2', 'memory' : 512, 'manufacturer' : 'Embest'},
            20:{'revision' : '0014', 'model' : 'Compute Module', 'pcb' : '1.0', 'memory' : 512, 'manufacturer' : 'Embest'},
            21:{'revision' : '0015', 'model' : 'A+', 'pcb' : '1.1', 'memory' : 256, 'manufacturer' : 'Embest'}
        }
        revision_model = ['A','B','A+','B+','Pi 2 B','Alpha','Compute Module','Zero','Pi 3 B','Zero','Compute Module 3','Zero W']
        revision_mem = [256,512,1024]
        revision_manufact = ['Sony','Egoman','Embest','Sony Japan','Embest']
        data = os.popen('cat /proc/cpuinfo').read().strip()
        match = re.compile(r'\nRevision\s*:\s*([\da-f]+)')
        final = match.search(data)
        final = final.group(1)
        if final:
            if final[0]=='1' or final[0]=='2':
                    final = final[1:]
            if len(final)== 4:
                    return revision[int(final, 16)]
            elif len(final) == 6 and final[0] != 'a' and final[0] != '9':
                    return revision[int(final[2:],16)]
            elif len(final) == 6 :
                    revisions = {
                        "revision" : final ,
                        "model" : revision_model[int(final[3:-1],16)], 
                        "pcb" : "1."+str(int(final[-1],16)),
                        "memory" : revision_mem[int((bin(int(final[0],16)).replace("0b","")[1:]),2)], 
                        "manufacturer" : revision_manufact[int(final[1:-4],16)]}
                    return revisions
        return "Not Found"
    
    def Serial(self):
        serial = os.popen('cat /proc/cpuinfo').read().strip()
        match = re.compile(r'\nSerial\s*:\s*([\da-f]+)')
        serialNo = match.search(serial)
        return serialNo.group(1)
    
    def MemoryUsage(self):
        memorytable = list(os.popen('free -bo 2>/dev/null || free -b').read().strip().split("\n"))
        if "available" in memorytable[0] :
            type,total, used, free, shared, buffers, available = re.split("\s+", memorytable[1])
            usage = int(round((int(total) - int(available)) / int(total) * 100))
            memory = {
                    "percent" : usage,
                    "total" : int(total),
                    "free"  : int(available),
                    "used"  : int(total) - int(available)
            }
            return memory
        type, total, used, free, shared, buffers, cached = re.split("\s+", memorytable[1])
        usage = int (round((int(used) - int(buffers) - int(cached)) / int(total) * 100))
        memory = {
                    "percent" : usage,
                    "total" : int(total),
                    "free"  : int(free) + int(buffers) + int(cached),
                    "used"  : int(used) - int(buffers) - int(cached)
        }
        return memory
    
    def SwapUsage(self):
        memorytable = list(os.popen('free -bo 2>/dev/null || free -b').read().strip().split("\n"))
        type,total, used, free = re.split("\s+", memorytable[2])
        usage = int(round(int(used) / int(total) * 100))
        swap = {
                    "percent" : usage,
                    "total" : int(total),
                    "free"  : int(free) ,
                    "used"  : int(used)
        }
        return swap
    
    def MemoryInfo(self):
        memorytable = list(os.popen('df -lT | grep -vE "tmpfs|rootfs|Filesystem|Dateisystem"').read().strip().split("\n"))
        devices = {}
        TotalDevice = {}
        totalSize = 0
        usedSize = 0
        totaldevices=[]
        for data in memorytable : 
                print(data)
                #device, _type, blocks, use, available, used, mountpoint = re.split("\s+", data)
                device=re.split("\s+", data)
                if device not in totaldevices :
                     totalSize += int(device[2]) * 1024
                     usedSize  += int(device[3]) * 1024
                devices["device"]= device[0]
                devices["type"] = device[1]
                devices["total"] = device[2]
                devices["used"] = device[3]
                devices["free"] = device[4]
                devices["percent"] = device[5]
                devices["mountpoint"] = device[6]
                totaldevices.append(devices.copy())
        #TotalDevice["total"]= totalSize
        #TotalDevice["used"] = usedSize
        #TotalDevice["free"] = totalSize - usedSize
        #TotalDevice["percent"] =  int(round((usedSize * 100 / totalSize)))
        #totaldevices.append(TotalDevice)   
        return totaldevices
    
    def UsbDevices(self):
        usb = list(os.popen('lsusb').read().strip().split("\n"))      
        usblist=[]
        for usbdevice in usb:
                match = re.compile(r'[0-9a-f]{4}:[0-9a-f]{4}\s+(.+)')
                final = match.search(usbdevice) 
                final = final.group(1) 
                if len(final) == 1 :
                    final = "Unknown"                  
                usblist.append(final)
        return usblist 
    
    def CheckLoggedIn(self,user,LoggedusersAll):
          for i in LoggedusersAll:
            if user in i:
                  return "yes"
            else:
                  return "No"
      
    def AllUsers(self):
      LoggedIn = list(os.popen('/usr/bin/who --ips').read().strip().split("\n"))
      Alluser = list(os.popen('/usr/bin/lastlog | grep -vE "Benutzername|Username" | cut -f 1 -d " "').read().strip().split("\n"))      
      usersLoggedIn = {}
      usersAll = []
      LoggedusersAll = []
      extractUserinfo = {}
      extraUserinfo = {}
      for user in LoggedIn : 
            extractUser = re.split("\s+", user)
            if len(extractUser) == 5:
                  usersLoggedIn[extractUser[0]]={
                       "port" :  extractUser[1],
                       "lastLogin": extractUser[2]+" "+extractUser[3],
                       "lastLoginAddress" : extractUser[4]
                  }
                  LoggedusersAll.append(usersLoggedIn.keys())
      for user in Alluser :
            userLastLoginInfo = os.popen('/usr/bin/last -i -f /var/log/wtmp | grep -m 1 ^'+user).read().strip()
            if not userLastLoginInfo:
                 userLastLoginInfo = os.popen('/usr/bin/last -i -f /var/log/wtmp.1 | grep -m 1 ^'+user).read().strip()

            if userLastLoginInfo:
                  extractUser = re.split("\s+", userLastLoginInfo)
                  extractUserinfo["username"] = user
                  extractUserinfo["userId"] = os.popen('id -u '+user).read().strip()
                  extractUserinfo["groupId"] = os.popen('id -g '+user).read().strip()
                  extractUserinfo["port"] = extractUser[1]
                  extractUserinfo["lastLoginAddress"] = extractUser[2]
                  extractUserinfo["lastLogin"] = extractUser[3]+" "+extractUser[4]+" "+extractUser[5]+" "+extractUser[6]
                  extractUserinfo["isLoggedIn"] = self.CheckLoggedIn(user,LoggedusersAll)
                  usersAll.append(extractUserinfo.copy())
            else:
                  extraUserinfo["username"] = user          
                  extraUserinfo["userId"] = os.popen('id -u '+user).read().strip()
                  extraUserinfo["groupId"] = os.popen('id -g '+user).read().strip()
                  extraUserinfo["port"] = ''
                  extraUserinfo["lastLoginAddress"] = ''
                  extraUserinfo["lastLogin"] = 0
                  extraUserinfo["isLoggedIn"] = self.CheckLoggedIn(user,LoggedusersAll)
                  usersAll.append(extraUserinfo.copy())
      usersAllInformation = sorted(usersAll, key = lambda i: i['username'])
      self.details['allusers'] = usersAllInformation
      return usersAllInformation
                
    
        

    
    
