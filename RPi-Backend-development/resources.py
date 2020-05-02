from flask_restful import Resource, reqparse
import models
import json
import werkzeug
from werkzeug.utils import secure_filename
import sys
from flask import Response,request,send_from_directory,make_response,abort
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)
from picontroller.RpiTaskmanager import Taskmanager
from picontroller.Services import Service
from picontroller.Setting import Setting
from picontroller.Log import Logs
from picontroller.Port import Ports
from picontroller.RpiFilemanager import Filemanager
from picontroller.RpiDetails import Details
from picontroller.RpiConfiguration import Configurations
from picontroller.Diskmanager import (CreatePartition,Check_external_devices,Delete_partition,Display_partition,Repair_filesystem,Partition_image)
import os
import datetime
import time
from run import app

headers={
    "Access-Control-Allow-Origin" : "*",
    "Access-Control-Allow-Headers" : "*",
    "Access-Control-Allow-Methods" : "*"
}

class IP(Resource):

    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    def get(self):
        ip_obj=Details(self.logger)
        run=ip_obj.Username()
        r=Response(response=json.dumps({"username":run}),status=200,mimetype="application/json")
        r.headers=headers
        return r

# class UserRegistration(Resource):
#     def post(self):
#         data = parser.parse_args()
        
#         if models.UserModel.find_by_username(data['username']):
#             return {'message': 'User {} already exists'.format(data['username'])}
        
#         new_user = models.UserModel(
#             username = data['username'],
#             password = models.UserModel.generate_hash(data['password'])
#         )
        
#         try:
#             new_user.save_to_db()
#             access_token = create_access_token(identity = data['username'])
#             refresh_token = create_refresh_token(identity = data['username'])
#             return {
#                 'message': 'User {} was created'.format(data['username']),
#                 'access_token': access_token,
#                 'refresh_token': refresh_token
#                 }
#         except:
#             return {'message': 'Something went wrong'}, 500


class UserLogin(Resource):

    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    def post(self):
        
        parser = reqparse.RequestParser()
        parser.add_argument('username', help = 'This field cannot be blank', required = True)
        parser.add_argument('password', help = 'This field cannot be blank', required = True)
        data = parser.parse_args()
        # username=request.form("username")
        # password=request.form("password")
        # current_user = models.UserModel.find_by_username(data['username'])
        obj=Setting()
        res = obj.authchecker(data["username"],data["password"])
        print(res)
        if res == "Valid password":
            if models.UserModel.find_by_username(data['username']):
                pass
            else:
                new_user = models.UserModel(
                    username = data['username'],
                    password = data['password']
                )   
                new_user.save_to_db()
        # if models.UserModel.verify_hash(data['password'], current_user.password):
            
            expires = datetime.timedelta(seconds=18000)
            expirestimesatmp = round(time.time()) + 18000
            access_token = create_access_token(identity = data["username"],expires_delta=expires)
            refresh_token = create_refresh_token(identity = data["username"])
            response={
                'message': 'Logged in as {}'.format(data["username"]),
                'access_token': access_token,
                'refresh_token': refresh_token,
                'expiry' : expirestimesatmp}
            r=Response(response=json.dumps(response),status=200,mimetype="application/json")
            r.headers=headers
            return r
        else:
            r=Response(response=json.dumps({'message': 'Wrong credentials'}),status=200,mimetype="application/json")
            r.headers=headers
            return r


# class UserLogoutAccess(Resource):
#     @jwt_required
#     def post(self):
#         jti = get_raw_jwt()['jti']
#         try:
#             revoked_token = models.RevokedTokenModel(jti = jti)
#             revoked_token.add()
#             return {'message': 'Access token has been revoked'}
#         except:
#             return {'message': 'Something went wrong'}, 500


# class UserLogoutRefresh(Resource):
#     @jwt_refresh_token_required
#     def post(self):
#         jti = get_raw_jwt()['jti']
#         try:
#             revoked_token = models.RevokedTokenModel(jti = jti)
#             revoked_token.add()
#             return {'message': 'Refresh token has been revoked'}
#         except:
#             return {'message': 'Something went wrong'}, 500


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def get(self):
        current_user = get_jwt_identity()
        expires = datetime.timedelta(seconds=3600)
        expirestimesatmp = round(time.time()) + 3600
        access_token = create_access_token(identity = current_user,expires_delta=expires)
        r=Response(response=json.dumps({'access_token': access_token,'expiry': expirestimesatmp}),status=200,mimetype="application/json")
        r.headers=headers
        return r


class Taskmanagement(Resource):

    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    @jwt_required
    def get(self):
        try :
            start = int(request.args.get("start"))
            limit = int(request.args.get("limit"))
            task_obj=Taskmanager()
            run=task_obj.GetProcesses()
            sorted_task=sorted(run, key = lambda i: i['ram'],reverse=True)
            count = len(sorted_task)
            if count < start or limit < 0:
                abort(404)
            print("length:",len(sorted_task))
            res = {
                "all_task":sorted_task[(start-1):(start-1 + limit)],
                "total" : count,
                "start":start,
                "limit":limit
            }
            r=Response(response=json.dumps(res),status=200,mimetype="application/json")
            r.headers=headers
            return r
        except Exception as e :
            print(e) 
            abort(404)


class ProcessAction(Resource):

    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')


    @jwt_required
    def get(self):
        pid=request.args.get("pid")
        command=request.args.get("command")
        pro_obj=Taskmanager()
        if command == "1":
            run=pro_obj.TerminateProcess(pid)
            r=Response(response=json.dumps({"result":run}),status=200,mimetype="application/json")
            r.headers=headers
            return r
        if command == "2":    
            run=pro_obj.KillProcess(pid)
            r=Response(response=json.dumps({"result":run}),status=200,mimetype="application/json")
            r.headers=headers
            return r
        
class ServiceManagement(Resource):
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    @jwt_required
    def get(self):
        ser_obj=Service()
        run=ser_obj.check_services()
        r=Response(response=json.dumps({"all_services":run}),status=200,mimetype="application/json")
        r.headers=headers
        print(r)
        return r

class ServiceDetails(Resource):

    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    @jwt_required
    def get(self):
        service_name=request.args.get("service")
        ser_obj=Service()
        run=ser_obj.service_details(service_name)
        r=Response(response=json.dumps({"details":run}),status=200,mimetype="application/json")
        r.headers=headers
        print(r)
        return r        

class ServiceAction(Resource):

    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    @jwt_required
    def get(self):
        command=request.args.get("command")
        service_name=request.args.get("service")
        ser_obj=Service()
        run=ser_obj.handle_service(command,service_name)
        r=Response(response=json.dumps({"result":run}),status=200,mimetype="application/json")
        r.headers=headers
        return r
        
class LogManagement(Resource):
    
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')
    
    @jwt_required
    def get(self):
        log_obj=Logs()
        run=log_obj.display_all_log_files()
        r=Response(response=json.dumps({"all_logs":run}),status=200,mimetype="application/json")
        r.headers=headers
        return r            

class LogFileOpen(Resource):
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')
   
    @jwt_required
    def get(self):
        file_name=request.args.get("file_name")
        log_obj=Logs()
        run=log_obj.display_specific_log_files(file_name)
        r=Response(response=json.dumps({"logs":run}),status=200,mimetype="application/json")
        r.headers=headers
        return r

class PortManagement(Resource):
    
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    
    @jwt_required
    def get(self):
        port_obj=Ports()
        run=port_obj.display_port()
        r=Response(response=json.dumps({"all_ports":run}),status=200,mimetype="application/json")
        r.headers=headers
        return r

class Traffic(Resource):
    
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    
    @jwt_required
    def get(self):
        connection = request.args.get("interface")
        traffic = Configurations()
        res = traffic.get_traffic(connection)
        r=Response(response=json.dumps(res),status=200,mimetype="application/json")
        r.headers=headers
        return r

class PortKill(Resource):
   
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    @jwt_required
    def get(self):
        pid=request.args.get("pid")
        port_obj=Ports()
        run=port_obj.kill_process(pid)
        r=Response(response=json.dumps({"result":run}),status=200,mimetype="application/json")
        r.headers=headers
        return r



class Networkinfo(Resource):
    
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    
    @jwt_required
    def get(self):
        obj = Configurations()
        res = {
            "netinfo" : obj.GetallNetworkConnections()
        }
        r=Response(response=json.dumps(res),status=200,mimetype="application/json")
        r.headers=headers
        return r  

class Specificnetworkinfo(Resource):
    
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    
    @jwt_required
    def get(self):
        interface = request.args.get("interface")
        net_obj = Configurations()
        res = net_obj.GetallNetworkConnections(interface,True)
        
        r=Response(response=json.dumps(res),status=200,mimetype="application/json")
        r.headers=headers
        return r  

class UserOperation(Resource):
    
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    
    @jwt_required
    def get(self):
        username=request.args.get("username")
        command=request.args.get("command")
        password=request.args.get("password")
        user_obj=Details()
        if command == "1":
            run=user_obj.CreateUser(username,password)
            r=Response(response=json.dumps({"result":run}),status=200,mimetype="application/json")
            r.headers=headers
            return r
        elif command == "2":    
            run=user_obj.DeleteUser(username)
            r=Response(response=json.dumps({"result":run}),status=200,mimetype="application/json")
            r.headers=headers
            return r
        elif command == "3":    
            run=user_obj.UpdatePassword(username,password)
            r=Response(response=json.dumps({"result":run}),status=200,mimetype="application/json")
            r.headers=headers
            return r



class Addwpa(Resource):
   
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    
    @jwt_required
    def get(self):
        ssid = request.args.get("ssid")
        password=request.args.get("password")
        wpa_obj = Configurations()
        res = wpa_obj.AddWpa(ssid,password)
        r=Response(response=json.dumps({"result":res}),status=200,mimetype="application/json")
        r.headers=headers
        return r

class Deletewpa(Resource):

    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')


    @jwt_required
    def get(self):
        ssid = request.args.get("ssid")
        wpa_obj = Configurations()
        res = wpa_obj.DeleteWpa(ssid)
        r=Response(response=json.dumps({"result":res}),status=200,mimetype="application/json")
        r.headers=headers
        return r

class Changewifi(Resource):

    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    @jwt_required
    def get(self):
        ssid = request.args.get("ssid")
        password=request.args.get("password")
        wpa_obj = Configurations()
        res = wpa_obj.changeWifi(ssid,password)
        r=Response(response=json.dumps({"result":res}),status=200,mimetype="application/json")
        r.headers=headers
        return r


class Spi(Resource):

    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    @jwt_required
    def get(self):
        command = request.args.get("command")
        spi_obj = Configurations()
        res = spi_obj.Spi(command)
        r=Response(response=json.dumps({"result":res}),status=200,mimetype="application/json")
        r.headers=headers
        return r
        
class I2c(Resource):

    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    @jwt_required
    def get(self):
        command = request.args.get("command")
        i2c_obj = Configurations()
        res = i2c_obj.I2c(command)
        r=Response(response=json.dumps({"result":res}),status=200,mimetype="application/json")
        r.headers=headers
        return r


class Wifilist(Resource):

    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    @jwt_required
    def get(self):
        wifi_obj = Configurations()
        res = wifi_obj.WifiList()
        r=Response(response=json.dumps({"result":res}),status=200,mimetype="application/json")
        r.headers=headers
        return r




class Ipmethodconfigure(Resource):

    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    @jwt_required
    def get(self):
        ip = request.args.get("ip")
        gateway = request.args.get("gateway")
        dns = request.args.get("dns")
        interface = request.args.get("interface")
        method = request.args.get("method")

        # interface_obj = Configurations()
        # res = interface_obj.WriteInterface(ip,gateway,dns,interface,method)
        r=Response(response=json.dumps({"result":True}),status=200,mimetype="application/json")
        r.headers=headers
        return r



class Wificontroller(Resource):

    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    @jwt_required
    def get(self):
        cmd = request.args.get("command")
        obj = Configurations()
        res = {
            "status" : obj.wificontrole(int(cmd))
        }
        r=Response(response=json.dumps(res),status=200,mimetype="application/json")
        r.headers=headers
        return r 



class Systemoperation(Resource):

    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    @jwt_required
    def get(self):
        command=request.args.get("command")
        sys_obj=Setting()
        run=sys_obj.system_operation(command)
        r=Response(response=json.dumps({"result":run}),status=200,mimetype="application/json")
        r.headers=headers
        return r 

class Cputemp(Resource):

    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')


    @jwt_required
    def get(self):
        cpu_obj=Details()
        run={
            "cputemp" : cpu_obj.CpuTemp(),
            "ramusage" : cpu_obj.MemoryUsage(),
            "cpuloadavg":cpu_obj.CpuLoadAvg(),
            "cpuusage":cpu_obj.cpuUsage()
        }

        r=Response(response=json.dumps({"result":run}),status=200,mimetype="application/json")
        r.headers=headers
        return r 
class Ramusage(Resource):

    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    @jwt_required
    def get(self):
        obj = Details()
        run = {
            "ramusage" : obj.MemoryUsage()
        }
        r = Response(response=json.dumps(run),status=200,mimetype="application/json")
        r.headers = headers
        return r
class Memoryusage(Resource):

    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    @jwt_required
    def get(self):
        memory_obj=Details()
        run=memory_obj.MemoryUsage()
        r=Response(response=json.dumps({"result":run}),status=200,mimetype="application/json")
        r.headers=headers
        return r

class Memoryinfo(Resource):

    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')


    @jwt_required
    def get(self):
        memory_obj=Details()
        run=memory_obj.MemoryInfo()
        r=Response(response=json.dumps({"result":run}),status=200,mimetype="application/json")
        r.headers=headers
        return r

class Cpuloadavg(Resource):

    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    @jwt_required
    def get(self):
        cpu_obj=Details()
        run=cpu_obj.CpuLoadAvg()
        r=Response(response=json.dumps({"result":run}),status=200,mimetype="application/json")
        r.headers=headers
        return r

class Swapusage(Resource):

    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    @jwt_required
    def get(self):
        cpu_obj=Details()
        run=cpu_obj.SwapUsage()
        r=Response(response=json.dumps({"result":run}),status=200,mimetype="application/json")
        r.headers=headers
        return r

class Revision(Resource):

    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    @jwt_required
    def get(self):
        cpu_obj=Details()
        run=cpu_obj.Revision()
        r=Response(response=json.dumps({"result":run}),status=200,mimetype="application/json")
        r.headers=headers
        return r

class Allusers(Resource):

    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    @jwt_required
    def get(self):
        cpu_obj=Details()
        run = cpu_obj.AllUsers()
        r=Response(response=json.dumps({"result":run}),status=200,mimetype="application/json")
        r.headers=headers
        return r

class Otherinfo(Resource):

    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    @jwt_required
    def get(self):
        cpu_obj=Details()
        run = {"cpuclock":cpu_obj.CpuClock(),
                "cpuminclock":cpu_obj.CpuMinClock(),
                "cpumaxclock":cpu_obj.CpuMaxClock(),
                "cputype":cpu_obj.CpuType(),
                "distribution":cpu_obj.Distribution(),
                "kernelversion":cpu_obj.KernelVersion(),
                "countrunningtask":cpu_obj.CountRunningTask(),
                "serial":cpu_obj.Serial()
        }
        r=Response(response=json.dumps({"result":run}),status=200,mimetype="application/json")
        r.headers=headers
        return r

class Displaypartition(Resource):

    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    @jwt_required
    def get(self):
        par_obj=Display_partition()
        ext_obj=Check_external_devices()
        run = {
            "partition":par_obj.get_partition(),
            "exteral":ext_obj.get_values()
        }
        r=Response(response=json.dumps({"result":run}),status=200,mimetype="application/json")
        r.headers=headers
        return r

class Shows(Resource):

    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    @jwt_required
    def get(self):
        drive_name=request.args.get("drivename")
        par_obj=Display_partition()
        run=par_obj.total_space(drive_name)
        res=par_obj.available_disk(drive_name)
        result={
            "result":run,
            "drive":res
        }
        r=Response(response=json.dumps(result),status=200,mimetype="application/json")
        r.headers=headers
        return r

class Createpartition(Resource):

    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    @jwt_required
    def get(self):
        drive_name=request.args.get("drive_name")
        command=request.args.get("command")
        part_command=request.args.get("part_command")
        # part_number=request.args.get("part_number")
        # first=request.args.get("first")
        # last=request.args.get("last")
        par_obj=CreatePartition()
        slot1=par_obj.create_partition(drive_name,command,part_command)
        r=Response(response=json.dumps({"result":slot1}),status=200,mimetype="application/json")
        r.headers=headers
        return r

class partNumber(Resource):

    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')


    @jwt_required
    def get(self):
        drive_name=request.args.get("drive_name")
        command=request.args.get("command")
        part_command=request.args.get("part_command")
        part_number=request.args.get("part_number")
        # first=request.args.get("first")
        # last=request.args.get("last")
        par_obj=CreatePartition()
        slot2=par_obj.part_number(drive_name,command,part_command,part_number)
        r=Response(response=json.dumps({"result":slot2}),status=200,mimetype="application/json")
        r.headers=headers
        return r

class First(Resource):

    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    @jwt_required
    def get(self):
        drive_name=request.args.get("drive_name")
        command=request.args.get("command")
        part_command=request.args.get("part_command")
        part_number=request.args.get("part_number")
        first=request.args.get("first")
        # last=request.args.get("last")
        par_obj=CreatePartition()
        slot3=par_obj.first(drive_name,command,part_command,part_number,first)
        r=Response(response=json.dumps({"result":slot3}),status=200,mimetype="application/json")
        r.headers=headers
        return r

class Last(Resource):

    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    @jwt_required
    def get(self):
        drive_name=request.args.get("drive_name")
        command=request.args.get("command")
        part_command=request.args.get("part_command")
        part_number=request.args.get("part_number")
        first=request.args.get("first")
        last=request.args.get("last")
        par_obj=CreatePartition()
        slot4=par_obj.last(drive_name,command,part_command,part_number,first,last)
        if slot4 == True:
            r=Response(response=json.dumps({"result":"Created success"}),status=200,mimetype="application/json")
            r.headers=headers
            return r
        else: 
            r=Response(response=json.dumps({"result":"Something went wrong"}),status=200,mimetype="application/json")
            r.headers=headers
            return r
            


####################### File folder operation ##############      

class Getfilefolder(Resource):
    
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    @jwt_required
    def get(self):
        path =request.args.get("path")
        hidden=request.args.get("hidden")
        obj = Filemanager()
        res = obj.AllDirs(PATH=path,hidden=hidden)
        r=Response(response=json.dumps(res),status=200,mimetype="application/json")
        # r.headers=headers
        return r 

class CheckExist(Resource):

    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')
    
    @jwt_required
    def get(self):
        obj = Filemanager(self.logger)
        res = {
            "status" : obj.FileDirExist
        }
        r=Response(response=json.dumps(res),status=200,mimetype="application/json")
        r.headers = headers
        return r

class Downlaodfile(Resource):

    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    @jwt_required
    def get(self):
        path = request.args.get("path")
        filepath = os.path.dirname(path) 
        filename = os.path.basename(path)
        print(filepath)
        print(filename)
        r = make_response(send_from_directory(filepath,filename,as_attachment=True))
        r.headers=headers
        return r

class Uploadfile(Resource):
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger') 

    @jwt_required 
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files')
        parser.add_argument('path', location='form')
        parser.add_argument('password', location='form')
        data = parser.parse_args()
        file = data['file']
        filename = secure_filename(file.filename)
        self.logger.debug("File name: %s",filename)
        path = data['path']
        file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
        password = data['password']
        PWD = models.UserModel.find_by_id(1).password
        if password:
            obj = Filemanager(self.logger,PWD)
        else:
            obj = Filemanager(self.logger)
        src = os.path.join(app.config['UPLOAD_FOLDER'] ,filename)
        dest = os.path.join(path,filename)
        data = obj.MoveFileDirs(src,dest)
        res = {}
        if data == "Permission denied":
            if os.path.exists(src):
                os.remove(src)
            res['flag'] = 0
            res['status']= False
            res['msg'] = data
        elif data == True:
            res['flag'] = 1
            res['status']= True
            res['msg'] = "successfuly uploaded"
        else:
            res['flag'] = 2
            res['status']= False
            res['msg'] = data
        r=Response(response=json.dumps(res),status=200,mimetype="application/json")
        r.headers = headers
        return r

class Createfile(Resource):
    
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    @jwt_required 
    def get(self):
        filename = request.args.get("filename")
        password = request.args.get("password")
        PWD = models.UserModel.find_by_id(1).password
        print(PWD)
        if password:
            obj = Filemanager(self.logger,PWD)
        else:
            obj = Filemanager(self.logger)
        data = obj.CreatFile(filename) 
        res = {} 
        if data == "Permission denied":
            res['flag'] = 0
            res['status']= False
            res['msg'] = data
        elif data == True:
            res['flag'] = 1
            res['status']= True
            res['msg'] = "successfuly created"
        else:
            res['flag'] = 2
            res['status']= False
            res['msg'] = data
        r=Response(response=json.dumps(res),status=200,mimetype="application/json")
        r.headers=headers
        return r

class Delfile(Resource):

    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')
    
    @jwt_required 
    def get(self):
        filename = request.args.get("filename")
        password = request.args.get("password")
        PWD = models.UserModel.find_by_id(1).password

        if password:
            obj = Filemanager(self.logger,PWD)
        else:
            obj = Filemanager(self.logger)
        res = {} 
        data = obj.DelFile(filename)
        if data == "Permission denied":
            res['flag'] = 0
            res['status']= False
            res['msg'] = data
        elif data == True:
            res['flag'] = 1
            res['status']= True
            res['msg'] = "successfuly deleted"
        else:
            res['flag'] = 2
            res['status']= False
            res['msg'] = data
      
        r=Response(response=json.dumps(res),status=200,mimetype="application/json")
        r.headers=headers
        return r

class Movefiledirs(Resource):
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    @jwt_required 
    def get(self):
        src = request.args.get("src")
        dest = request.args.get("dest")
        password = request.args.get("password")
        PWD = models.UserModel.find_by_id(1).password
        if password:
            obj = Filemanager(self.logger,PWD)
        else:
            obj = Filemanager(self.logger)
        res = {} 
        data = obj.MoveFileDirs(src,dest)
        if data == "Permission denied":
            res['flag'] = 0
            res['status']= False
            res['msg'] = data
        elif data == True:
            res['flag'] = 1
            res['status']= True
            res['msg'] = "successfuly performed"
        else:
            res['flag'] = 2
            res['status']= False
            res['msg'] = data
        r=Response(response=json.dumps(res),status=200,mimetype="application/json")
        r.headers=headers
        return r

class Copyfile(Resource):
    
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    @jwt_required 
    def get(self):
        src = request.args.get("src")
        dest = request.args.get("dest")
        password = request.args.get("password")
        PWD = models.UserModel.find_by_id(1).password
        if password:
            obj = Filemanager(self.logger,PWD)
        else:
            obj = Filemanager(self.logger)
        res = {} 
        data = obj.CopyFile(src,dest)
        if data == "Permission denied":
            res['flag'] = 0
            res['status']= False
            res['msg'] = data
        elif data == True:
            res['flag'] = 1
            res['status']= True
            res['msg'] = "successfuly copied"
        else:
            res['flag'] = 2
            res['status']= False
            res['msg'] = data
        r=Response(response=json.dumps(res),status=200,mimetype="application/json")
        r.headers=headers
        return r

class Createdir(Resource):
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    @jwt_required 
    def get(self):
        dirname = request.args.get("dirname")
        password = request.args.get("password")
        PWD = models.UserModel.find_by_id(1).password
        if password:
            obj = Filemanager(self.logger,PWD)
        else:
            obj = Filemanager(self.logger)
        res = {}
        data = obj.CreatDirs(dirname)
        if data == "Permission denied":
            res['flag'] = 0
            res['status']= False
            res['msg'] = data
        elif data == True:
            res['flag'] = 1
            res['status']= True
            res['msg'] = "successfuly created"
        else:
            res['flag'] = 2
            res['status']= False
            res['msg'] = data
        r=Response(response=json.dumps(res),status=200,mimetype="application/json")
        r.headers=headers
        return r

class Deldir(Resource):
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')
    @jwt_required 
    def get(self):
        dirname = request.args.get("dirname")
        password = request.args.get("password")
        PWD = models.UserModel.find_by_id(1).password
        
        if password:
            obj = Filemanager(self.logger,PWD)
        else:
            obj = Filemanager(self.logger)
        res = {}
        data = obj.DelDirs(dirname)
        if data == "Permission denied":
            res['flag'] = 0
            res['status']= False
            res['msg'] = data
        elif data == True:
            res['flag'] = 1
            res['status']= True
            res['msg'] = "successfuly deleted"
        else:
            res['flag'] = 2
            res['status']= False
            res['msg'] = data
        r=Response(response=json.dumps(res),status=200,mimetype="application/json")
        r.headers=headers
        return r

class Copydir(Resource):
    
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    @jwt_required 
    def get(self):
        src = request.args.get("src")
        dest = request.args.get("dest")
        password = request.args.get("password")
        PWD = models.UserModel.find_by_id(1).password
        if password:
            obj = Filemanager(self.logger,PWD)
        else:
            obj = Filemanager(self.logger)
        res = {}
        data = obj.CopyDir(src,dest)
        if data == "Permission denied":
            res['flag'] = 0
            res['status']= False
            res['msg'] = data
        elif data == True:
            res['flag'] = 1
            res['status']= True
            res['msg'] = "successfuly copied"
        else:
            res['flag'] = 2
            res['status']= False
            res['msg'] = data
        r=Response(response=json.dumps(res),status=200,mimetype="application/json")
        r.headers=headers
        return r
        
        
class Readfile(Resource):
    
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    @jwt_required
    def get(self):
        password = request.args.get("password")
        PWD = models.UserModel.find_by_id(1).password
        path = request.args.get("path")
        if password:
            obj = Filemanager(self.logger,PWD)
        else:
            obj = Filemanager(self.logger)
        res = obj.ReadFile(path)
        r=Response(response=json.dumps(res),status=200,mimetype="application/json")
        r.headers=headers
        return r
        
class WriteFile(Resource):

    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    @jwt_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('data', help = 'This field cannot be blank', required = True)
        parser.add_argument('path', help = 'This field cannot be blank', required = True)
        parser.add_argument('password', help = 'This field cannot be blank')  
        alldata = parser.parse_args() 
        data= alldata["data"]
        self.logger.debug(data)
        path=alldata["path"]
        password = alldata["password"]
        PWD = models.UserModel.find_by_id(1).password
        if password:
            obj = Filemanager(self.logger,PWD)
        else:
            obj = Filemanager(self.logger)
        res ={}
        data = obj.WriteFile(data,path)
        if data == "Permission denied":
            res['flag'] = 0
            res['status']= False
            res['msg'] = data
        elif data == True:
            res['flag'] = 1
            res['status']= True
            res['msg'] = "successfuly Saved"
        else:
            res['flag'] = 2
            res['status']= False
            res['msg'] = data
        r=Response(response=json.dumps(res),status=200,mimetype="application/json")
        r.headers=headers
        return r        

######################################################################
