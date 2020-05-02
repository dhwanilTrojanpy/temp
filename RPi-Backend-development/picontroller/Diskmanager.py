import os
import subprocess
import re
class Check_external_devices:
    """
    Module Check_external_devices

    Give detailed information about external drives.
    """
    
    def list_media_devices(self):
        """
        List of all attached drives.
        """
        with open("/proc/partitions", "r") as f:
            devices = []
            
            for line in f.readlines()[2:]: # skip header lines
                words = [ word.strip() for word in line.split() ]
                minor_number = int(words[1])
                device_name = words[3]
                
                if (minor_number % 16) == 0:
                    path = "/sys/class/block/" + device_name
                    
                    if os.path.islink(path):
                        if os.path.realpath(path).find("/usb") > 0:
                            devices.append("/dev/" + device_name)
            
            return devices

    def list_files(self,root, indent=1):
        """
        List of files in drives.
        `root` Root path
        `indent` For giving space(default=1)
        """
        for filename in os.listdir(root):
            path = os.path.join(root, filename)
            if os.path.isfile(path):
                print("-" * indent, filename)
            elif os.path.isdir(path):
                print("+" * indent, filename)
                self.list_files(path, indent + 1)

    def get_device_name(self,device):
        """
        Gives name of the device
        `device` Device name
        """ 
        return os.path.basename(device)


    def get_device_block_path(self,device):
        """
        Gives block path of the device
        `device` Device name
        """
        return "/sys/block/%s" % self.get_device_name(device)


    def get_media_path(self,device):
        """
        Gives path of the device
        `device` Device name
        """
        return "/media/" + self.get_device_name(device)


    def get_partition(self,device):
        """
        Shows all partitions
        `device` Device name
        """
        os.system("sudo fdisk -l %s > output" % device)
        with open("output", "r") as f:
            data = f.read()
            return data.split("\n")[-2].split()[0].strip()


    def is_mounted(self,device):
        """
        Check whether device is mounted or not
        `device` Device name
        """
        return os.path.ismount(self.get_media_path(device))


    def mount_partition(self,partition, name="usb"):
        """
        For mounting the device
        `name` Device name(default=usb)
        """
        path = self.get_media_path(name)
        if not self.is_mounted(path):
            os.system("mkdir -p " + path)
            os.system("mount %s %s" % (partition, path))

    def unmount_partition(self,name="usb"):
        """
        For unmounting the device
        `name` Device name(default=usb)
        """
        path = self.get_media_path(name)
        if self.is_mounted(path):
            os.system("umount " + path)


    def mount(self,device, name=None):
        """
        For mounting the device
        `device` Device name
        'name' Variable which will be assigned by variable 'device'(default=None)
        """
        if not name:
            name = self.get_device_name(device)
        self.mount_partition(self.get_partition(device), name)

    def unmount(self,device, name=None):
        """
        For unmounting the device
        `device` Device name
        'name' Variable which will be assigned by variable 'device'(default=None)
        """
        if not name:
            name = self.get_device_name(device)
        self.unmount_partition(name)


    def is_removable(self,device):
        """
        Check whether drive is remoable or not
        `device` Device name
        """
        path = self.get_device_block_path(device) + "/removable"
        
        if os.path.exists(path):
            with open(path, "r") as f:
                return f.read().strip() == "1"
        
        return None


    def get_size(self,device):
        """
        Shows size of the drive
        `device` Device name
        """
        path = self.get_device_block_path(device) + "/size"
        
        if os.path.exists(path):
            with open(path, "r") as f:
                
                return int(f.read().strip()) * 512
        
        return -1


    def get_model(self,device):
        """
        Shows model of the drive
        `device` Device name
        """
        path = self.get_device_block_path(device) + "/device/model"
        
        if os.path.exists(path):
            with open(path, "r") as f:
                return f.read().strip()
        return None

    def get_vendor(self,device):
        """
        Shows vendor name of the device
        `device` Device name
        """
        path = self.get_device_block_path(device) + "/device/vendor"
        
        if os.path.exists(path):
            with open(path, "r") as f:
                return f.read().strip()
        return None

    def get_values(self):
        """
        TO display all values
        """
        devices = self.list_media_devices()
        deviceList={}
        deviceFinal=[]
        for device in devices:
            deviceList["drive"]=self.get_device_name(device)
            deviceList["mounted"]="Yes" if self.is_mounted(device) else "No"
            deviceList["removable"]="Yes" if self.is_removable(device) else "No"
            deviceList["size(GB)"]= "%.2f" % (self.get_size(device) / 1024 ** 3)
            deviceList["model"]=self.get_model(device)
            deviceList["vendor"]=self.get_vendor(device)
            deviceFinal.append(deviceList.copy())
        return deviceFinal    

class Delete_partition:
    """
    Module `Delete_partition`

    Use to delte any partition
    """
    def delete(self,drive_name,command,part_number=None):
        """
        For deleting any partition.
        """
        if command=="Delete":
            partitions=subprocess.Popen(["sudo","fdisk","{}".format(drive_name)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            output=partitions.communicate(b"d")[0].decode()
            print(output)
            if part_number:
                partitions=subprocess.Popen(["sudo","fdisk","{}".format(drive_name)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
                msg="d\n{}\nw".format(part_number)
                encoded_msg = msg.encode('utf-8')
                output=partitions.communicate(encoded_msg)[0].decode()
                return True             
        
        # drives={}
        # drivesList=[]
        # with open("/proc/partitions", "r") as f:
        #     for line in f.readlines()[2:]:
        #         split = re.split('[\s]+',line)
        #         if split[0]=='':
        #             del split[0]    
        #         drives["major"]=split[0]
        #         drives["minor"]=split[1]
        #         drives["block"]=split[2]
        #         drives["namee"]=split[3]
            #         drivesList.append(drives.copy())
            #     print(drivesList)        
        # drive_name=input("enter drive name:")
        # minor_number=input("enter minor_number:")

        # os.system("sudo parted "+drive_name+" rm "+minor_number)

class Display_partition:
    """
    Module `Display_partition`
    Display all internal partitions of the main Harddrive
    """
    def  __init__(self):    
        self.commandList=[]
        self.newCommand={}
        self.split=" "
        commands= os.popen ("sudo parted -l").read().strip().splitlines()[1:2]
        for command in commands:
            self.split= re.split('[\s]+',command)
        self.split=self.split[1][:-1]
        print(self.split)

    def get_partition(self):
        """
        Display all partitions present in internal drive.
        """
        commandList=[]
        newCommand={}
        commands= os.popen ("sudo fdisk -l {}".format(self.split)).read().strip().splitlines()[8:]
        
        for command in commands:
            if not command:
                continue
            split = re.split('[\s]+',command)
            if split[0]=='':
                del split[0]            
            newCommand["device"]=split[0]
            newCommand["start"]=split[1]
            newCommand["end"]=split[2] 
            newCommand["sectors"]=split[3]   
            newCommand["size"]=split[4]
            newCommand["type"]=split[5]
            commandList.append(newCommand.copy())
        return commandList


    def total_space(self,drive_name):
        partList=[]
        partDic={}
        partitions=subprocess.Popen(["sudo","fdisk","{}".format(drive_name)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        output=partitions.communicate(b"p")[0].decode().splitlines()[6]
        if "Command (m for help): " in output:   
            partList.append(output[22:49])    
        return partList

    def available_disk(self,drive_name):
        partList=[]
        partDic={}
        partitions=subprocess.Popen(["sudo","fdisk","{}".format(drive_name)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        output=partitions.communicate(b"p")[0].decode().splitlines()[14:-2]
        for line in output:
            split=re.split('[\s]+',line)
            partDic["device"]=split[0]
            partDic["start"]=split[1]
            partDic["end"]=split[2]
            partDic["sectors"]=split[3]
            partDic["size"]=split[4]
            partList.append(partDic)    
        return partList

class CreatePartition():
    
    # def create_partition(self,drive_name,command,part_command=None,part_number=None,first=None,last=None):
    #     """
    #     Create_Partition is used to resize partition available in harddrive
    #     """
    #     partList=[]
    #     partDic={}
    #     if command=="create" and part_command=="extended":
    #         partitions=subprocess.Popen(["sudo","fdisk","{}".format(drive_name)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    #         msg="n\ne\n{}\n".format(part_number)
    #         encoded_msg = msg.encode('utf-8')
    #         output=partitions.communicate(encoded_msg)[0].decode()
    #         print(output)
    #         if first:
    #             partitions=subprocess.Popen(["sudo","fdisk","{}".format(drive_name)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    #             msg=msg+str(first)
    #             encoded_msg = msg.encode('utf-8')
    #             output=partitions.communicate(encoded_msg)[0].decode()
    #             print(output)
    #             if last:
    #                 partitions=subprocess.Popen(["sudo","fdisk","{}".format(drive_name)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    #                 msg=msg+str(first)+"\n"+last+"\nw"        
    #                 encoded_msg = msg.encode('utf-8')
    #                 output=partitions.communicate(encoded_msg)[0].decode()
    #                 print(output)
    #             else:
    #                 return "Error: enter LAst value.."
        
    #         else:
    #             return "Error: enter First value.."
        
        
    #     if command=="make" and part_command=="primary":
    #         partitions=subprocess.Popen(["sudo","fdisk","{}".format(drive_name)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    #         msg="n\np\n{}\n".format(part_number)
    #         encoded_msg = msg.encode('utf-8')
    #         output=partitions.communicate(encoded_msg)[0].decode()
    #         print(output)
    #         if first:
    #             partitions=subprocess.Popen(["sudo","fdisk","{}".format(drive_name)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    #             msg=msg+str(first)
    #             encoded_msg = msg.encode('utf-8')
    #             output=partitions.communicate(encoded_msg)[0].decode()
    #             print(output)
    #             if last:
    #                 partitions=subprocess.Popen(["sudo","fdisk","{}".format(drive_name)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    #                 msg=msg+str(first)+"\n"+last+"\nw"        
    #                 encoded_msg = msg.encode('utf-8')
    #                 output=partitions.communicate(encoded_msg)[0].decode()
    #                 print(output)
    #             else:
    #                 return "Error: enter LAst value.."
        
    #         else:
    #             return "Error: enter First value.."

    def create_partition(self,drive_name,command,part_command):
        """
        Create_Partition is used to resize partition available in harddrive
        """
        partList=[]
        partDic={}
        if command=="create" and part_command=="extended":
            partitions=subprocess.Popen(["sudo","fdisk","{}".format(drive_name)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            msg="n\ne"
            encoded_msg = msg.encode('utf-8')
            output=partitions.communicate(encoded_msg)[0].decode().splitlines()[-1] 
            partList.append(output[20:])    
            return partList
        elif command=="create" and part_command=="primary":
            partitions=subprocess.Popen(["sudo","fdisk","{}".format(drive_name)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            msg="n\np"
            encoded_msg = msg.encode('utf-8')
            output=partitions.communicate(encoded_msg)[0].decode().splitlines()[-1] 
            partList.append(output[20:])    
            return partList    
    
    def part_number(self,drive_name,command,part_command=None,part_number=None):
        partitions=subprocess.Popen(["sudo","fdisk","{}".format(drive_name)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        msg="n\ne\n{}\n".format(part_number)
        encoded_msg = msg.encode('utf-8')
        output=partitions.communicate(encoded_msg)[0].decode().splitlines()[-2]
        line=output.split(":")
        return line[2]

    def first(self,drive_name,command,part_command=None,part_number=None,first=None):
        partitions=subprocess.Popen(["sudo","fdisk","{}".format(drive_name)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        msg="n\ne\n{}\n".format(part_number)
        msg=msg+str(first)
        encoded_msg = msg.encode('utf-8')
        output=partitions.communicate(encoded_msg)[0].decode().splitlines()[-2]
        return output[99:]

    def last(self,drive_name,command,part_command=None,part_number=None,first=None,last=None):                
        partitions=subprocess.Popen(["sudo","fdisk","{}".format(drive_name)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        msg="n\ne\n{}\n".format(part_number)
        msg=msg+str(first)+"\n"+last+"\nw"        
        encoded_msg = msg.encode('utf-8')
        output=partitions.communicate(encoded_msg)[0].decode().splitlines()[10]
        return True    
           

class Repair_filesystem:
    """
    Module `Repair_filesystem`
    Use to repair filesystem of devices 
    """
    def repair(self,drive_name):
        """
        Use to repair filesystem.
        """
        cmdList=[]
        cmdDic={}
        commands=os.popen("lsblk").read().strip().splitlines()
        for command in commands:
            split = re.split('[\s]+',command)
            if split[0]=='':
                del split[0]    
            cmdDic["name"]=split[0]
            cmdDic["maj:min"]=split[1]
            cmdDic["rm"]=split[2]
            cmdDic["size"]=split[3]
            cmdList.append(cmdDic.copy())
        print(cmdList)    
        
        fsckDic={}
        umountDic={}
        resultDic={}
        mountDic={}

        umnt=os.popen("sudo umount "+drive_name).read().strip().splitlines()
        for word in umnt:
            umountDic["output"]=word
        print(umountDic)

        cmd=os.popen("sudo fsck "+drive_name).read().strip().splitlines()
        for line in cmd:
            fsckDic["output"]=line
        print(fsckDic)

        result=os.popen("echo $?").read().strip().splitlines()
        for ans in result:
            resultDic["output"]=ans
        print(resultDic)
        
        if result==0:
            print("No errors")
            mnt=os.popen("sudo mount "+drive_name).read().strip().splitlines()
            for word in mnt:
                mountDic["output"]=word
            print(mountDic)

        else:
            mountDic["output"]="{} errors were there".format(result)
        print(mountDic)    

class Partition_image:
    """
    Module `Partition_image`
    Use to create and restore partition image of the drive 
    """
    def create_image(self):
        """
        To create partition image of th disk 
        """
        drive=input("drive name:") 
        path=input("enter path:")
        os.system("sudo dd if={} conv=sync,noerror bs=64K | gzip -c > {}".format(drive,path))  
        
    def restore_image(self):
        """
        To restore partition image of th disk 
        """
        drive=input("drive name:") 
        path=input("enter path:")
        os.system(" gunzip -c {} | dd of={}".format(path,drive)) 