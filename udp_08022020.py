import socket
import datetime
from influxdb import InfluxDBClient
import struct
import json

# InfluxDB
client = InfluxDBClient(host='150.162.19.148', port=8086, database='db_smf_50')
print(client.get_list_database())
#client.switch_database('db_smf_50')
print(client.get_list_measurements())

# Multicast
#MCAST_GRP = '224.0.1.1'
#MCAST_PORT = 4713
#IS_ALL_GROUPS = True

#
UDP_IP = "150.162.19.217"
UDP_PORT = 4728

sock = socket.socket(socket.AF_INET, #internet
                    socket.SOCK_DGRAM) # UDP

sock.bind((UDP_IP, UDP_PORT))

#sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
#sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

'''if IS_ALL_GROUPS:
    # on this port, receives ALL multicast groups
    sock.bind(('', MCAST_PORT))
else:
    # on this port, listen ONLY to MCAST_GRP
    sock.bind((MCAST_GRP, MCAST_PORT)) '''

#mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)

#sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

num_pmu = 0
phnmr = [3]
stn = []
annmr = 0
dgnmr = 0
idcode = []


configuration_frame = {
        "MAIN": 
            {
            #'SYNC': None,
            #'FRAMESIZE': None,
            #'IDCODE': None,
            #'SOC': None,
            #'FRACSEC': None,
            #'NUM_PMU': None
        },
        "TERMINALS": [{
            'PHNMR': 3
        }]
    }

data_frame_rec = {
    "MAIN": 
        {
        #'SYNC': None,
        #'FRAMESIZE': None,
        #'IDCODE': None,
        #'SOC': None,
        #'FRACSEC': None
    },
    "TERMINALS": [{
        #'STAT': None,
        #'PHASORS': [{
            #'MOD_A': None,
            #'ANG_A': None,
            #'MOD_B': None,
            #'ANG_B': None,
            #'MOD_C': None,
            #'ANG_C': None
       # }],
        #'FREQ': None,
        #'DFREQ': None
    }]
}

# atualiza os canais a cada minuto com o frame de configuracao
def atualiza_canais():

    # incremento para pular para as próximas medições
    inc = 0

    # Sincronismo
    configuration_frame['MAIN']['SINC'] = struct.unpack('!h', data_frame1[0:2])[0] 

    # Frame Size
    configuration_frame['MAIN']['FRAMESIZE'] = struct.unpack('!h', data_frame1[2:4])[0]
    print('Framesize: ', configuration_frame['MAIN']['FRAMESIZE'])

    # ID Code do Stream
    configuration_frame['MAIN']['IDCODE'] = struct.unpack('!h', data_frame1[4:6])[0]

     # SOC
    configuration_frame['MAIN']['SOC'] = struct.unpack('!i', data_frame1[6:10])[0]

     # FRACSEC
    configuration_frame['MAIN']['FRACSEC'] = struct.unpack('!i', data_frame1[10:14])[0]

    # converte o número de PMUs (hexadecimal) do frame de configuração para int (decimal)
    configuration_frame['MAIN']['NUM_PMU'] = struct.unpack('!h', data_frame1[18:20])[0] 
    print('Num PMUs: ', configuration_frame['MAIN']['NUM_PMU'])
    print('SOC: ', configuration_frame['MAIN']['SOC'])
    print('FRACSEC: ', configuration_frame['MAIN']['FRACSEC'])
    
    print('config_frame: ', data_frame1)
   

    for i in range(0, configuration_frame['MAIN']['NUM_PMU']-1):

        configuration_frame['TERMINALS'].append({
            'STN': struct.unpack('!16s', data_frame1[(inc+20):(inc+36)])[0].decode().strip(),
            'IDCODE': struct.unpack('!h', data_frame1[(inc+36):(inc+38)])[0],
            'PHNMR': struct.unpack('!h', data_frame1[(inc+40):(inc+42)])[0],
            
        })
        print('STN: ', struct.unpack('!16s', data_frame1[(inc+20):(inc+36)])[0].decode())
        inc += 30 + 20 * int(configuration_frame['TERMINALS'][i+1]['PHNMR'])

global received_command_frame
received_command_frame = 0
while received_command_frame != '31':
    # Aguarda o frame de configuração
    data_frame1 = sock.recv(10240)
    data_frame = data_frame1.hex()

    # converte tuple to string hexadecimal (hex())
    received_command_frame = struct.unpack('!s', data_frame1[1:2])[0].hex()
    print("aguardando")
    SOC = data_frame1[6:10].hex()
    
    print(
        datetime.datetime.fromtimestamp(
            int(SOC, 16)
        ).strftime('%Y-%m-%d  %H:%M:%S')
    )
     
# atualiza os canais (function)
print("Chegou o frame de configuração!")
print('Hexadecimal_DATA: ', data_frame1)
print('-------')
# print('Frame: ', data_frame)
# print('------')
atualiza_canais()
print('aqui o config: ', configuration_frame)

data_frame1 = 0
data_frame = 0
# Aquisição do frame de dados
while True:
    data_frame1 = sock.recv(10240)
    data_frame = data_frame1.hex()
    received_command_frame = struct.unpack('!s', data_frame1[1:2])[0].hex()

    if (received_command_frame == '31'):
        atualiza_canais()

    else:
        # Adquire o SOC e passa para o dict
        data_frame_rec['MAIN']['SOC'] = struct.unpack('!i', data_frame1[6:10])[0]

        # Adquire o FRACSEC e passa para o dict
        data_frame_rec['MAIN']['FRACSEC'] = struct.unpack('!i', data_frame1[10:14])[0]

        TIME_BASE = 16777216 # 2^24 para compatibilida da norma IEC 61850 (Está na norma IEEE C37.118)
        frac_sec = data_frame_rec['MAIN']['FRACSEC']  / TIME_BASE

        SOC_DATA = data_frame_rec['MAIN']['SOC'] + frac_sec
        SOC_DATA_conv =  datetime.datetime.fromtimestamp(
                SOC_DATA
            ).strftime('%Y-%m-%dT%H:%M:%S.%f%Z')
            
        print('SOC: ',
            datetime.datetime.fromtimestamp(
                SOC_DATA
            ).strftime('%Y-%m-%dT%H:%M:%S.%f%Z')
        )

        SOC_3339 = datetime.datetime.fromtimestamp(SOC_DATA).timestamp()

        json_body = [
            {
                "measurement": 0,# STN_PMU,
                "tags": {
                    "IDCODE_PMU": 0,
                    "STAT": 0, 
                },
                "time": SOC_DATA_conv,
                "fields": {
                    'MOD_A': 0,
                    'ANG_A': 0,
                    'MOD_B': 0,
                    'ANG_B': 0,
                    'MOD_C': 0,
                    'ANG_C': 0,
                    'FREQ': 0,
                    'DFREQ': 0
                }
            }
        ]


        # incremento para pular para as próximas medições
        inc = 0
        for i in range(0, configuration_frame['MAIN']['NUM_PMU'] - 1):
           
            inc_freq_dfreq = 8 * int(configuration_frame['TERMINALS'][i+1]['PHNMR'])

            fasores = {
                'IDCODE_PMU': configuration_frame["TERMINALS"][i+1]["IDCODE"],
                #'STN_PMU': configuration_frame["TERMINALS"][i+1]["STN"],
                'STAT': struct.unpack('!h', data_frame1[(inc+14):(inc+16)])[0],
                'PHASORS': {
                    'MOD_A': struct.unpack('!f', data_frame1[(inc+16):(inc+20)])[0],
                    'ANG_A': struct.unpack('!f', data_frame1[(inc+20):(inc+24)])[0],
                    'MOD_B': struct.unpack('!f', data_frame1[(inc+24):(inc+28)])[0],
                    'ANG_B': struct.unpack('!f', data_frame1[(inc+28):(inc+32)])[0],
                    'MOD_C': struct.unpack('!f', data_frame1[(inc+32):(inc+36)])[0],
                    'ANG_C': struct.unpack('!f', data_frame1[(inc+36):(inc+40)])[0]    
                },
                'FREQ': struct.unpack('!f', data_frame1[(inc+inc_freq_dfreq+16):(inc+inc_freq_dfreq+20)])[0],
                'DFREQ': struct.unpack('!f', data_frame1[(inc+20):(inc+24)])[0]
            }


            data_frame_rec['TERMINALS'].append(fasores)

            json_body = [
                {
                    "measurement": configuration_frame["TERMINALS"][i+1]["STN"],
                    "tags": {
                        "IDCODE_PMU": configuration_frame["TERMINALS"][i+1]["IDCODE"],
                        "STAT": struct.unpack('!h', data_frame1[(inc+14):(inc+16)])[0], 
                    },
                    "time": SOC_DATA_conv,
                    "fields": {
                        'MOD_A': struct.unpack('!f', data_frame1[(inc+16):(inc+20)])[0],
                        'ANG_A': struct.unpack('!f', data_frame1[(inc+20):(inc+24)])[0],
                        'MOD_B': struct.unpack('!f', data_frame1[(inc+24):(inc+28)])[0],
                        'ANG_B': struct.unpack('!f', data_frame1[(inc+28):(inc+32)])[0],
                        'MOD_C': struct.unpack('!f', data_frame1[(inc+32):(inc+36)])[0],
                        'ANG_C': struct.unpack('!f', data_frame1[(inc+36):(inc+40)])[0],
                        'FREQ': struct.unpack('!f', data_frame1[(inc+inc_freq_dfreq+16):(inc+inc_freq_dfreq+20)])[0],
                        'DFREQ': struct.unpack('!f', data_frame1[(inc+20):(inc+24)])[0]
                    }
                }
            ]

            client.write_points(json_body)
            print('---------------------')
            print('GRAVANDO: ', json_body)
            #json_body[0]["fields"].update({configuration_frame["TERMINALS"][i+1]["STN"] : {'MOD_A': struct.unpack('!f', data_frame1[(inc+16):(inc+20)])[0]}})
            # json_body[0]["fields"].update({configuration_frame["TERMINALS"][i+1]["STN"] : fasores})

            inc += 10 + 8 * int(configuration_frame['TERMINALS'][i+1]['PHNMR'])
            
            if i == 2:
                break
        
