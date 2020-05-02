import os
import shlex
import re
import time
import sys

class Configurations:            
    
    def GetWpa(self):
        allssid=[]
        wpa_supplicant = os.popen('sudo cat /etc/wpa_supplicant/wpa_supplicant.conf').read().strip()
        count = wpa_supplicant.count('ssid')
        totalssid = list(wpa_supplicant.split('network'))
        del totalssid[0]
        for total in totalssid:
                pos_start = total.find('ssid="') + 6
                pos_end = total.find('"',pos_start)
                wifissid = total[pos_start:pos_end]
                allssid.append(wifissid)
        return allssid

    
    def ChangeHostname(self,hostname=None):
        host = os.popen('cat /etc/hosts').read().strip()
        if not host:
            return False
        newhost =re.sub(r"(127\.0\.1\.1[\s]+)(.+)$",r'\1%s'%hostname,host)
        command = 'echo {} | sudo /bin/su -c "cat > /etc/hosts"'.format(shlex.quote(newhost))
        os.system(command)
        command = 'echo {} | sudo /bin/su -c "cat > /etc/hostname"'.format(shlex.quote(hostname))
        os.system(command)
        return True
    
    
    def NetworkInterface(self,interface_name):
        networks = list(os.popen("ip address show | grep '{}' | grep 'inet'".format(interface_name)).read().split())

        network = {
            'method' : 'dynamic' if "dynamic" in networks else 'static',
            'ip' :  networks[networks.index('inet') + 1 ] }
        return network
        # for network in networks:
        #         if network and network[0].strip() !='#':s
        #             if network[0:4]=='auto':
        #                     data['auto'] = True
        #                     interfaces[network[5:].strip()]= data.copy()
        #                     continue
        #             if network[0:10]=='allow-auto':
        #                     data['allow-auto'] = True
        #                     interfaces[network[10:].strip()]= data.copy() 
        #                     continue
        #             if network[0:13]=='allow-hotplug':
        #                     data.pop('auto', None)
        #                     data['allow-hotplug'] = True
        #                     interfaces[network[13:].strip()]= data.copy()
        #                     continue
        #             if network[0:5]=='iface': 
        #                     interface = network.split(' ')
        #                     isInterface = interface[1].strip()
        #                     data['protocol'] = interface[2]
        #                     data['method'] = interface[3]
        #                     interfaces[isInterface]= data.copy()
        #                     continue
        #             if isInterface:
        #                     match = re.search(r'^[\s]*([\w\d\-]*)[\s]+(.*)$',network)
        #                     matchdata[ match.group(1)] = match.group(2)
        #                     data['iface']= matchdata.copy()
        #                     interfaces[isInterface]= data.copy() 

        #         elif network and network[0].strip() =='#':
        #             comment = network
        #         elif network and network[0].strip() != '':
        #             others = network
            
        # return interfaces
        

    def GetallNetworkConnections(self,interface_name=None,flag=False):
        try:
            command =''
            output = {}
            allInterfaces = []
            if interface_name:
                network_interface = list(os.popen('/sbin/ifconfig | grep -E -o "^[[:alnum:][:punct:]]*" | grep -E -v "(lo)" | sed "s/:$//"').read().strip().split('\n'))
                command='/sbin/ifconfig '+ interface_name 
                streams = os.popen(command).read().strip().split('-#-')   
            else:    
                network_interface = list(os.popen('/sbin/ifconfig | grep -E -o "^[[:alnum:][:punct:]]*" | grep -E -v "(lo)" | sed "s/:$//"').read().strip().split('\n'))
                
                for interface in network_interface:
                        command += '/sbin/ifconfig '+ interface +(' && echo "-#-" && ' if network_interface[len(network_interface)-1] != interface else '')
                streams = list(os.popen(command).read().strip().split('-#-'))
            for i,stream in enumerate(streams):
                wirelessOption = {}
                interface = interface_name if interface_name else network_interface[i]
                ipAdress = re.search(r'inet(?:[ ]+(?:addr\:)?)([\w\.]+)',stream)
                macAdress = re.search(r'(?:HWaddr|ether) ([\w\:]+)',stream)
                byterecv = re.search(r'RX(?:.*?)bytes[:| ]([\d]+)',stream)
                bytetrans = re.search(r'TX(?:.*?)bytes[:| ]([\d]+)',stream)
                packetrecv = re.search(r'RX(?:.*?)packets[:| ]([\d]+)',stream)
                packettrans = re.search(r'TX(?:.*?)packets[:| ]([\d]+)',stream)
                
                output0 = interface
                if output0[0:4] == "wlan":
                    wirelessinterface = os.popen('/sbin/iwconfig {}'.format(output0)).read().strip()
                    if 0 == wirelessinterface.count('Not-Associated'):
                            posConfig_start = wirelessinterface.find('ESSID:"') + 7
                            posConfig_end = wirelessinterface.find('"',posConfig_start)
                            wirelessOption['ssid']= wirelessinterface[posConfig_start:posConfig_end].strip()
                            posConfig_start = wirelessinterface.find('Access Point:') + 13
                            posConfig_end = wirelessinterface.find('Bit Rate',posConfig_start)
                            wirelessOption['mac']= wirelessinterface[posConfig_start:posConfig_end].strip()
                            
                            posConfig_start = wirelessinterface.find('Signal level=') + 13
                            posConfig_end = wirelessinterface.find('/100',posConfig_start)
                            if posConfig_end == -1 :
                                posConfig_end = wirelessinterface.find(' dBm',posConfig_start)
                                signal = int(wirelessinterface[posConfig_start:posConfig_end])
                                if signal <= -100:
                                    wirelessOption['signal']= 0
                                elif signal >= -50:
                                        wirelessOption['signal']= 100
                                else:
                                        wirelessOption['signal'] = 2 * (signal+100)
                                
                            else:
                                wirelessOption['signal'] = int(wirelessinterface[posConfig_start:posConfig_end])                 
                
                if flag==True:
                    data = self.NetworkInterface(interface_name)
                    output['sent']= bytetrans.group(1)  
                    output['receive']= byterecv.group(1)
                    output['option'] = wirelessOption  
                    output['packets'] = {
                        "sent": packettrans.group(1),
                        "received" : packetrecv.group(1)
                    }
                    output['ip'] = data['ip']
                    output['method'] = data['method']
                    return output
                else:
                    output['interface']=interface
                    output['mac'] =   macAdress.group(1).upper() if macAdress else None
                    output['ip'] = ipAdress.group(1) if ipAdress else None   
                    output['status'] =  True if ipAdress else False
                    output['Action'] = "btn"
                    allInterfaces.append(output.copy())                       
            return allInterfaces
        except Exception as e: 
            return e

    def get_traffic(self,request):
        """
        Get the traffic for the specified interface
        """
        try:
            pipe = os.popen("cat /proc/net/dev |" + "grep " + request + "| awk '{print $1, $9}'")
            data = pipe.read().strip().split(':', 1)[-1]
            pipe.close()
            current_time = round(time.time())
            print(current_time)
            if not data[0].isdigit():
                pipe = os.popen("cat /proc/net/dev |" + "grep " + request + "| awk '{print $2, $10}'")
                data = pipe.read().strip().split(':', 1)[-1]
                pipe.close()

            data = data.split()

            sent = int(data[0]) 
            rec = int(data[1])

            all_traffic = {'sent': sent, 'recieve': rec,'time' : current_time}

            data = all_traffic

        except Exception as err:
            data = str(err)

        return data

    def wificontrole(self,command):
        """ command=`1` for turn on wifi
            command=`0` for turn off wifi
         """
        print(command)
        if command == 1:
            os.system("sudo rfkill unblock wifi")
            return True
        if command == 0:
            os.system("sudo rfkill block wifi")
            return True
        else: 
            return "Invalid command"

    def changeWifi(self,ssid=None,passwaord=None):
        wpa_supplicant = os.popen('sudo cat /etc/wpa_supplicant/wpa_supplicant.conf').read().strip()
        pos_start = wpa_supplicant.find('ssid="') + 6
        pos_end = wpa_supplicant.find('"',pos_start)
        wifissid = wpa_supplicant[pos_start:pos_end]
        pos_start = wpa_supplicant.find('psk="') + 5
        pos_end = wpa_supplicant.find('"',pos_start)
        wifipsk = wpa_supplicant[pos_start:pos_end]
        newwpa = wpa_supplicant.replace(wifissid,ssid,1)
        
        newwpa = newwpa.replace(wifipsk,passwaord,1)
        command = 'echo {} | sudo /bin/su -c "cat > /etc/wpa_supplicant/wpa_supplicant.conf"'.format(shlex.quote(newwpa))
        status = os.popen(command).read().strip()
        if status=='':
            return True
        else:
            return False
    
    
    def AddWpa(self,ssid=None,password=None):
        wpa_supplicant = os.popen('sudo cat /etc/wpa_supplicant/wpa_supplicant.conf').read().strip()
        if ssid in self.GetWpa():
            return "Already There"
        else:
            pos_start = wpa_supplicant.find('ssid="') + 6
            pos_end = wpa_supplicant.find('"',pos_start)
            wifissid = wpa_supplicant[pos_start:pos_end]
            newnetwork = 'network={\n    ssid="'+ssid+'"'+'\n    psk="'+password+'"'+'\n}'
            newwpa = wpa_supplicant +'\n\n'+ newnetwork
            command = 'echo {} | sudo /bin/su -c "cat > /etc/wpa_supplicant/wpa_supplicant.conf"'.format(shlex.quote(newwpa))
            status = os.popen(command).read().strip()
            if status=='':
                  return True
            else:
                  return False
        
    
    def DeleteWpa(self,ssid=None):
        wpa_supplicant = os.popen('sudo cat /etc/wpa_supplicant/wpa_supplicant.conf').read().strip()
        if ssid not in self.GetWpa():
            return "Not Found"
        else:
            pos_start = wpa_supplicant.find(ssid) + 10
            pos_end = wpa_supplicant.find('}',pos_start) 
            psk = wpa_supplicant[pos_start:pos_end]
            print("psk-->>",psk)
            pos_start = psk.find('psk="')+5
            pos_end = psk.find('"',pos_start)
            password = psk[pos_start:pos_end]
            print("password-->",password)
            newnetwork = 'network={\n    ssid="'+ssid+'"'+'\n    psk="'+password+'"'+'\n    key_mgmt=WPA-PSK\n}'
            print(newnetwork)
            newwpa = wpa_supplicant.replace(newnetwork,'')
            print("newwpa-->",newwpa)
            command = 'echo {} | sudo /bin/su -c "cat > /etc/wpa_supplicant/wpa_supplicant.conf"'.format(shlex.quote(newwpa))
            status = os.popen(command).read().strip()
            if status=='':
                return True
            else:
                return False
        
    def Spi(self,command=None):
        spi = os.popen('sudo cat /boot/config.txt').read().strip()
        os.system("sed -i '/#dtparam=spi/d' /boot/config.txt")
        os.system("sed -i '/dtparam=spi/d' /boot/config.txt")
        # start = spi.find('dtparam=s') +9
        # end = spi.find('\n',start)
        # spi = spi.replace(spi[start:end],'pi='+command)
        spi='"dtparam=spi=on"'
        command = 'echo {} | sudo /bin/su -c "cat > /boot/config.txt"'.format(spi)
        # command = 'echo {} | sudo /bin/su -c "cat > /boot/config.txt"'.format(shlex.quote(spi))
        print("command-->>",command)
        status = os.popen(command).read().strip()
        if status=='':
            return True
        else:
            return False
        
    def I2c(self,command=None):
            i2c = os.popen('sudo cat /boot/config.txt').read().strip()
            start = i2c.find('dtparam=i2c_a') + 13
            end = i2c.find('\n',start)
            i2c = i2c.replace(i2c[start:end],'rm='+command)
            command = 'echo {} | sudo /bin/su -c "cat > /boot/config.txt"'.format(shlex.quote(i2c))
            status = os.popen(command).read().strip()
            if status=='':
                  return True
            else:
                  return False
            
    def WriteInterface(self,ip=None,gateway=None,dns=None,interface=None,method=None,protocol='inet'):
            file = os.popen('sudo cat /etc/olddhcpcd.conf').read().strip()
            oldInterfaces = os.popen('sudo cat /etc/network/interfaces').read().strip()
            if method=='static':
                newstr = '\ninterface '+interface+'\nstatic ip_address='+ip+'\nstatic routers='+gateway+'\nstatic domain_name_servers='+dns
                file += newstr
                command = 'echo {} | sudo /bin/su -c "cat > /etc/olddhcpcd.conf"'.format(shlex.quote(file))
                status = os.popen(command)
                networkinterface = self.NetworkInterface(interface)
                oldMethod = networkinterface['method']
                oldInterfaces = oldInterfaces.replace('iface '+interface+' inet '+oldMethod,'iface '+interface+' inet manual',1)
                # status = os.popen('echo {} | sudo /bin/su -c "cat > /etc/network/interfaces"'.format(shlex.quote(oldInterfaces))).read()
                if status == '':
                    return True
                else:
                    return False
            if method == 'dhcp':
                oldnewstr = '\ninterface '+interface+'\nstatic ip_address='+ip+'\nstatic routers='+gateway+'\nstatic domain_name_servers='+dns
                newstr = '#interface '+interface+'\n#static ip_address='+ip+'\n#static routers='+gateway+'\n#static domain_name_servers='+dns
                file = file.replace(oldnewstr,newstr,1)
                print(file)
                command = 'echo {} | sudo /bin/su -c "cat > /etc/olddhcpcd.conf"'.format(shlex.quote(file))
                status = os.popen(command)
                networkinterface = self.NetworkInterface(interface)
                oldMethod = networkinterface['method']
                print(oldMethod)
                oldInterfaces = oldInterfaces.replace('iface '+interface+' inet '+oldMethod,'iface '+interface+' inet dhcp',1)
                status = os.popen('echo {} | sudo /bin/su -c "cat > /etc/network/interfaces"'.format(shlex.quote(oldInterfaces))).read()
                
                if status == '':
                    return True
                else:
                    return False

            
        
    def WifiList(self):
        wifiList=[] 
        wlan={}
        # networkInterface = self.NetworkInterface()
        # print(networkInterface)
        # for keys in networkInterface:

        #         if keys[0:4] != 'wlan' :
        #             continue
        #         print(keys)
        streamWlan = os.popen('sudo /sbin/iwlist wlan0 scan').read().strip()
        streamWlan = streamWlan.splitlines()
        streamWlan = [i.strip() for i in streamWlan]
        streamWlan = [i.replace('Encryption key:','').replace("ESSID:",'').replace('\"','').replace('Channel:','').replace('Cell ','') 
                    for i in streamWlan if i.find('ESSID') != -1 or i.find('Channel:') != -1 or i.find('key')!=-1 or i.find('Address') != -1]      
        streamWlan =[streamWlan[i : i+4] for i in range(0, len(streamWlan), 4)]
        # sys.stderr.write(str(streamWlan))                   
        for i in streamWlan:
            wlan['ssid']=i[3]
            wlan['macadress']=i[0].replace(' - Address: ','')[3: ] if len(i[0].replace(' - Address: ',''))>19 else i[0].replace(' - Address: ','')[2:]
            wlan['channel'] = i[1]
            wlan['security']= 'WPA2' if i[2]=='on' else 'not secure' 
            wifiList.append(wlan.copy())   
        return wifiList
         
    
    
    
        