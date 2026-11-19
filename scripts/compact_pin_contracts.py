"""Manufacturer pin names/types for custom R1 symbols (no upstream code copied)."""
CONTRACTS={
'U3':{str(i):(n,t) for i,n,t in [(1,'VINA_internal','passive'),(2,'GND','power_in'),(3,'FB','input'),(4,'VOUT','power_out'),(5,'VOUT','passive'),(6,'L2','passive'),(7,'L2','passive'),(8,'L1','passive'),(9,'L1','passive'),(10,'VIN','power_in'),(11,'VIN','passive'),(12,'EN','input'),(13,'PS_SYNC','input'),(14,'PG','open_collector'),(15,'PGND_EP','power_in')]},
'U4':{'1':('IN','power_in'),'2':('GND','power_in'),'3':('EN','input'),'4':('NC','no_connect'),'5':('OUT','power_out')},
'U5':{str(i):(n,'power_in' if i in [1,2,3,16,17,18,20,21,24,25,28,29,33] else 'output' if i in [12,19,22,23,26,27,30,32] else 'bidirectional' if i==9 else 'input') for i,n in enumerate(['IOVSS','IOVDD','DVDD','NC','DIN','WCLK','BCLK','MCLK','SDA','SCL','VOL_MICDET','MICBIAS','AIN1','AIN2','NC','AVSS','AVDD','DVSS','SPKM','SPKVSS','SPKVDD','SPKP','SPKM','SPKVDD','SPKVSS','SPKP','HPL','HPVDD','HPVSS','HPR','RESET_N','GPIO1','EP'],1)},
'U6':{'1':('CLK','input'),'2':('D','input'),'3':('Q_N','output'),'4':('GND','power_in'),'5':('Q','output'),'6':('CLR_N','input'),'7':('PRE_N','input'),'8':('VCC','power_in')},
'U7':{'1':('A','input'),'2':('B','input'),'3':('GND','power_in'),'4':('Y','output'),'5':('VCC','power_in')},
'U9':{str(i):(n,'power_in' if i in [8,16] else 'open_collector' if i==13 else 'bidirectional' if i in [4,5,6,7,9,10,11,12,15] else 'input') for i,n in enumerate(['A0','A1','A2','P0','P1','P2','P3','GND','P4','P5','P6','P7','INT_N','SCL','SDA','VCC'],1)},
'U10':{str(i):(n,'passive') for i,n in enumerate(['IO1','GND','IO2','IO2','VBUS','IO1'],1)},
'U11':{'1':('SW','open_collector'),'2':('GND','power_in'),'3':('FB','input'),'4':('EN','input'),'5':('VIN','power_in')},
'J3':{'1':('SLEEVE_MICDET','passive'),'2':('TIP_L','passive'),'3':('RING1_R','passive'),'4':('RING2_GND','passive')},
'J8':{str(i):(n,'passive') for i,n in enumerate(['GND','RESET_N','SCL','RS_DC','CS_N','SDA_MOSI','SDO_MISO','GND','VDD','LEDA','K1','K2','K3','K4','XL_NC','YU_NC','XR_NC','YD_NC'],1)}
}
