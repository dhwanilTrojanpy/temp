import os
import re
import time
import signal



class Taskmanager:
      
    def SecondsFromTime(self,time):
        split = re.split('[-:]+', time)
        if len(split)== 4 :
                return int(split[0])*86400 + int(split[1])*3600 + int(split[2])*60 + int(split[3])
        elif len(split)== 3 : 
                return int(split[0])*3600 + int(split[1])*60 + int(split[2])
        return int(split[0])*60 + int(split[1])
        
    def Status(self,status):
        if 'S' in status :
                return "Sleep"
        if 'D' in status:
                return "Uninterruptible"
        if 'R' in status:
                return "Running"
        if 'Z' in status:
                return "Zombie"
        return ''
    
    def GetProcesses(self):
        processList = []   
        newProcessess = {}
        processes = os.popen('ps axo pid,ppid,user,stat,pcpu,pmem,etime,time,comm | tail -n +2').read().strip().splitlines()
        for process in processes:
                if not process:
                    continue
                split = re.split('[\s]+', process)
                if split[0] == '':
                    del split[0]
                newProcessess['pid'] = split[0]
                newProcessess['ppid'] = split[1]
                newProcessess['user'] = split[2]
                newProcessess['status'] = self.Status(split[3])
                newProcessess['cpu'] = split[4]+'0%'
                newProcessess['ram'] = split[5]+'0%'
                newProcessess['starttime'] = round(time.time()) - self.SecondsFromTime(split[6])
                newProcessess['runtime'] = split[7]
                newProcessess['command'] = split[8]
                newProcessess['action'] = 'btn'
                processList.append(newProcessess.copy())
        self.totalProcesses = len(processList)
        print(processList)
        return processList
    
    def TotalProcesses(self):
        return len(self.GetProcesses())
    
    def Running(self):
        processes =  self.GetProcesses()
        count=0
        for i in processes:
                if i['status'] == 'Running':
                    count += 1 
        return count
                
    def TerminateProcess(self,pid=None):
        try:
                # status = os.kill(int(pid), signal.SIGTERM)
                status=  os.system("kill -15 {}".format(pid))
                if not status:
                    return True
        except ProcessLookupError:
                return False
    
    def KillProcess(self,pid=None):
        try:
                # status = os.kill(int(pid), signal.SIGKILL)
                status=  os.system("kill -9 {}".format(pid))
                if not status:
                    return True
        except ProcessLookupError:
                return False