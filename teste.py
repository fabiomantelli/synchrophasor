
a = 'pmu'
configuration_frame = [{
        "MAIN": 
            {
            'SYNC': 3,
            'FRAMESIZE': 0,
            'IDCODE': 0,
            'SOC': 0,
            'FRACSEC': 0,
            'TIME_BASE': 0,
            'NUM_PMU': 0
        },
        "TERMINALS": {
            a: {
                'STN': 2,
                'IDCODE': 0,
                'PHNMR': 0,
                'ANNMR': 0,
                'DGNMR': 0,
                'PHUNIT': 0,
                'FNOM': 0,
                'CFGCNT': 0
        }
            
        }
    }]
teste = {
     
            'STN': 10,
            'IDCODE': 0,
            'PHNMR': 0,
            'ANNMR': 0,
            'DGNMR': 0,
            'PHUNIT': 0,
            'FNOM': 0,
            'CFGCNT': 0
      
}
configuration_frame[0]['TERMINALS'].update({'fabio': teste})
print('configuration_frame: ', configuration_frame)

data_frame_rec = {
        "MAIN": 
            {
            'SYNC': None,
            'FRAMESIZE': None,
            'IDCODE': None,
            'SOC': None,
            'FRACSEC': None
        },
        "TERMINALS": [{
            'STAT': None,
            'PHASORS': {
                'MOD_A': 5,
            },
            'FREQ': None,
            'DFREQ': None
        },{
            'STAT': None,
            'PHASORS': {
                'MOD_A': 10,
            },
            'FREQ': None,
            'DFREQ': None
        },{
            'STAT': None,
            'PHASORS': {
                'MOD_A': 695,
            },
            'FREQ': None,
            'DFREQ': None
        }]
    }


teste = {
    'STAT': None,
    'PHASORS': {
        'MOD_A': 543,
    },
    'FREQ': None,
    'DFREQ': None
}

#print('terminals: ', data_frame_rec["TERMINALS"])
data_frame_rec["TERMINALS"].append(teste)

#print('terminals após append: ', data_frame_rec["TERMINALS"])

#data_frame_rec["TERMINALS"][0]["PHASORS"][0]["MOD_A"] = 5
