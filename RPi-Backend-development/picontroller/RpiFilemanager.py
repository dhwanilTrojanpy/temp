import os
from os import path
import time
import shutil
import shlex
from subprocess import Popen, PIPE, STDOUT
from pathlib import Path

class Filemanager:

      def __init__(self,logger=None,password=None):
            self.password = password
            self.log = logger
      
      def FileDirExist(self,path):
            status = path.exists(path)
            return status

      def FileSize(self,path):
            try:
                  return os.stat(path).st_size
            except FileNotFoundError:
                  return 'File NoT Found'

      def Getfilelist(self,dirs,fullpath,password):
            datalist = []
            data = {} 
            for i in dirs:
                  data['name'] = i
                  filestatus = os.popen("if [ -f {} ]; then echo 1; else echo 0;fi".format(fullpath+i)).read().strip()
                  if filestatus=='1':
                        data['type'] = "file" 
                        data["size"] = self.FileSize(fullpath+i)
                        data['item'] = 0     
                  else:
                        data['type'] = "folder"
                        data['size'] = 0
                        files= os.popen("echo {}| sudo -S ls -a {}".format(password,fullpath+i)).read().splitlines()
                        data["item"] =len(files)          
                  data['path'] = fullpath+i
                  data['secure'] = not(os.access(fullpath+i,os.W_OK))      
                  datalist.append(data.copy())  
            return datalist

      def AllDirs(self,PATH='/home',hidden=None,password='goldenmace'):
            lastchar = PATH[len(PATH)-1]
            fullpath = PATH if lastchar=="/" else PATH + '/'
            if hidden:
                  # dirs = os.listdir(PATH)
                  dirs = os.popen("echo {}| sudo -S ls -a {}".format(password,PATH)).read().splitlines()
                  if dirs[0]=='.' and dirs[1]=='..':
                        dirs.pop(0)
                        dirs.pop(0)
                  print(dirs)
                  return self.Getfilelist(dirs,fullpath,password)  
                       
            else :
                  # dirs = [f for f in os.listdir(PATH) if not f.startswith('.')]
                  dirs = os.popen("echo {}| sudo -S ls {}".format(password,PATH)).read().splitlines()
                  return self.Getfilelist(dirs,fullpath,password)  
            
      def GetModifyTime(self,path):
            try:
                  return os.stat(path).st_mtime
            
            except FileNotFoundError:
                  return 'File NoT Found'
      


      def ReturnHandler(self,status,error): 
            if error == b'' or error == None:
                  return True
            else:
                  d_error = error.decode().split(':')
                  d_error = d_error[len(d_error) - 1].strip()
                  return d_error

      def CreatFile(self,fileName):
            if self.password:
                  pipe = Popen('echo {} | sudo -S touch {}'.format(self.password,fileName), shell=True, stdin=PIPE, stdout=PIPE, 
                              stderr=PIPE, close_fds=True)
                  status,error= pipe.communicate()
                  pipe.stdout.close()
                  return self.ReturnHandler(status,error)
            else:
                  pipe = Popen('touch  {}'.format(fileName), shell=True, stdin=PIPE, stdout=PIPE, 
                              stderr=PIPE, close_fds=True)
                  status,error= pipe.communicate()
                  pipe.stdout.close()
                  return self.ReturnHandler(status,error)
      
      def DelFile(self,filePath): 
            if self.password:
                  pipe = Popen('echo {} | sudo -S rm {}'.format(self.password,filePath), shell=True, stdin=PIPE, stdout=PIPE, 
                              stderr=PIPE, close_fds=True)
                  status,error= pipe.communicate()
                  pipe.stdout.close()
                  return self.ReturnHandler(status,error)
            else:
                  pipe = Popen('rm  {}'.format(filePath), shell=True, stdin=PIPE, stdout=PIPE, 
                              stderr=PIPE, close_fds=True)
                  status,error= pipe.communicate()
                  pipe.stdout.close()
                  return self.ReturnHandler(status,error)


      def DelDirs(self,dirName):
            if self.password:
                  pipe = Popen('echo {} | sudo -S rm -rf {}'.format(self.password,dirName), shell=True, stdin=PIPE, stdout=PIPE, 
                              stderr=PIPE, close_fds=True)
                  status,error= pipe.communicate()
                  pipe.stdout.close()
                  return self.ReturnHandler(status,error)
            else:
                  pipe = Popen('rm -rf {}'.format(dirName), shell=True, stdin=PIPE, stdout=PIPE, 
                              stderr=PIPE, close_fds=True)
                  status,error= pipe.communicate()
                  pipe.stdout.close()
                  return self.ReturnHandler(status,error)
      
      def MoveFileDirs(self,oldPath, newPath):
            if self.password: 
                  pipe = Popen('echo {}|sudo -S mv {} {}'.format(self.password,oldPath,newPath), shell=True, stdin=PIPE, stdout=PIPE, 
                                          stderr=PIPE, close_fds=True)
                  status,error= pipe.communicate()
                  pipe.stdout.close()
                  return self.ReturnHandler(status,error)
            else:
                  pipe = Popen('mv {} {}'.format(oldPath,newPath), shell=True, stdin=PIPE, stdout=PIPE, 
                                          stderr=PIPE, close_fds=True)
                  status,error= pipe.communicate()
                  pipe.stdout.close()
                  return self.ReturnHandler(status,error)
      
      def CreatDirs(self,dirPath):
            if self.password:
                  pipe = Popen('echo {} | sudo -S mkdir {}'.format(self.password,dirPath), shell=True, stdin=PIPE, stdout=PIPE, 
                              stderr=PIPE, close_fds=True)
                  
                  status,error= pipe.communicate()
                  pipe.stdout.close()
                  return self.ReturnHandler(status,error)
            else:
                  pipe = Popen('mkdir {}'.format(dirPath), shell=True, stdin=PIPE, stdout=PIPE, 
                              stderr=PIPE, close_fds=True)
                  
                  status,error= pipe.communicate()
                  pipe.stdout.close()
                  return self.ReturnHandler(status,error)
      
      def CopyFile(self,source,dest):
            if self.password:
                  pipe = Popen('echo {} | sudo -S cp -f {} {} '.format(self.password,source,dest), shell=True, stdin=PIPE, stdout=PIPE, 
                              stderr=PIPE,close_fds=True)

                  status,error= pipe.communicate()
                  pipe.stdout.close()
                  return self.ReturnHandler(status,error)

            else:
                  pipe = Popen('cp -f {} {} '.format(source,dest), shell=True, stdin=PIPE, stdout=PIPE, 
                              stderr=PIPE,close_fds=True)

                  status,error= pipe.communicate()
                  pipe.stdout.close()
                  return self.ReturnHandler(status,error)
                  
      def CopyDir(self,source,dest):
            if self.password:
                  pipe = Popen('echo {} | sudo -S cp -rf {} {} '.format(self.password,source,dest), shell=True, stdin=PIPE, stdout=PIPE, 
                              stderr=PIPE,close_fds=True)

                  status,error= pipe.communicate()
                  pipe.stdout.close()
                  return self.ReturnHandler(status,error)

            else:
                  pipe = Popen('cp -rf {} {} '.format(source,dest), shell=True, stdin=PIPE, stdout=PIPE, 
                              stderr=PIPE,close_fds=True)

                  status,error= pipe.communicate()
                  pipe.stdout.close()
                  return self.ReturnHandler(status,error)
                  
      def ReadFile(self,path):
            if self.password:      
                  editDic={}
                  edit=Popen("echo {} | sudo -S cat {}".format(self.password,path), stdin=PIPE, stdout=PIPE, 
                              stderr=STDOUT,shell=True,close_fds=True) 
                  editDic["result"] = edit.communicate()[0].decode()   
                  return editDic
            else:
                  editDic={}
                  edit=Popen("cat {}".format(path), stdin=PIPE, stdout=PIPE, 
                              stderr=STDOUT,shell=True,close_fds=True) 
                  editDic["result"] = edit.communicate()[0].decode()   
                  return editDic
                  
      def WriteFile(self,data,path):
            if self.password:     
                  self.log.debug(path) 
                  pipe = Popen('echo {} | sudo -S echo {} | tee {}'.format(self.password,shlex.quote(data),path), shell=True, stdin=PIPE, stdout=PIPE, 
                              stderr=STDOUT, close_fds=True)
                  status,error= pipe.communicate()
                  pipe.stdout.close()
                  return self.ReturnHandler(status,error)
            else:
                  pipe = Popen('echo {} | tee {}'.format(shlex.quote(data),path), shell=True, stdin=PIPE, stdout=PIPE, 
                              stderr=STDOUT, close_fds=True)
                  status,error= pipe.communicate()
                  pipe.stdout.close()
                  return self.ReturnHandler(status,error)
                  