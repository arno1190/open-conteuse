#!/usr/bin/env python3
"""Compact R1 engineering source. Coordinates in case XY; KiCad adds 30mm origin.
No geometry or price here is a physical validation or a supplier quotation.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'hardware/compact-r1'
SOURCES={
 'mcu':'https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf',
 'codec':'https://www.ti.com/lit/ds/symlink/tlv320dac3100.pdf',
 'charger':'https://www.ti.com/lit/ds/symlink/bq24074.pdf',
 'regulator':'https://www.ti.com/lit/ds/symlink/tps63020.pdf',
 'amp':'https://www.analog.com/media/en/technical-documentation/data-sheets/MAX98357A-MAX98357B.pdf',
 'latch':'https://www.ti.com/lit/ds/symlink/sn74lvc1g74.pdf',
 'gate':'https://www.ti.com/lit/ds/symlink/sn74lvc1g08.pdf',
 'io':'https://www.ti.com/lit/ds/symlink/tca9534.pdf',
 'ldo':'https://www.ti.com/lit/ds/symlink/tlv755p.pdf',
 'boost':'https://www.ti.com/lit/ds/symlink/tps61040.pdf',
 'jack':'https://jp.sameskydevices.com/product/resource/sj-4351x-smt.pdf',
 'nfc':'https://www.elechouse.com/product/pn532-mini/',
 'nfc_manual':'https://www.elechouse.com/docs/pn5321-mini/',
 'lcd':'https://www.ronboe.com/shop/rb024d18n01b1/',
 'cell':'https://www.adafruit.com/product/258',
 'speaker':'https://puiaudio.com/product/speakers-and-receivers/as01508ao-wp-r',
}
# Parts: exact buying identity, per-unit EUR allowance, case placement, physical envelope,
# footprint, net map. Passive pin names are their literal terminal numbers.
def design(variant):
 parts=[]
 def add(ref,mpn,fp,xy,pins,size,cost,section,source=None,angle=0):
  parts.append(dict(ref=ref,mpn=mpn,footprint=fp,xy=xy,pins={str(k):v for k,v in pins.items()},size=size,cost_eur=cost,section=section,source=SOURCES.get(source,source or ''),angle=angle))
 def r(ref,value,xy,a,b,section='logic'):
  # Yageo RC0603FR-07 series exact E96 resistance suffix.
  code={'10k':'10KL','100k':'100KL','2.2k':'2K2L','5.1k':'5K1L','1.78k':'1K78L','3.24k':'3K24L','3.57k':'3K57L','3.01k':'3K01L','20k':'20KL','120':'120RL','100':'100RL','1M':'1ML','332k':'332KL','187k':'187KL','27':'27RL','1k':'1KL'}[value]
  add(ref,'RC0603FR-07'+code,'Resistor_SMD:R_0603_1608Metric',xy,{1:a,2:b},[1.6,.8,.55],[.01,.06],section,'https://www.yageo.com/en/Product/Index/product_type/chip-resistors');parts[-1]['value']=value
 def c(ref,value,xy,a,b='GND',section='power'):
  spec={'100n':('GRM188R71C104KA01D','C_0603_1608Metric',[1.6,.8,.9],[.02,.08]),'1u':('GRM188R61A105KA61D','C_0603_1608Metric',[1.6,.8,.9],[.03,.12]),'10u':('GRM21BR61A106KE19L','C_0805_2012Metric',[2,1.25,1.35],[.06,.2]),'22u':('GRM21BR61A226ME44L','C_0805_2012Metric',[2,1.25,1.35],[.12,.35]),'100u':('GRM32ER60J107ME20L','C_1210_3225Metric',[3.2,2.5,2.7],[.5,1.2])}[value]
  add(ref,spec[0],'Capacitor_SMD:'+spec[1],xy,{1:a,2:b},spec[2],spec[3],section,'https://www.murata.com/en-global/products/capacitor/mlcc');parts[-1]['value']=value
 # Fixed module pad-to-GPIO contract, not DevKit header numbering.
 gp={4:'IO4',5:'IO5',6:'IO6',7:'IO7',15:'IO15',16:'IO16',17:'IO17',18:'IO18',8:'IO8',19:'USB_DN',20:'USB_DP',3:None,46:None,9:'IO9',10:'SD_CS',11:'SPI_MOSI',12:'SPI_SCK',13:'SPI_MISO',14:'LCD_CS',21:'CODEC_IRQ',47:'SPK_REQUEST',48:'LED_STATUS',45:None,0:'BOOT_N',35:None,36:None,37:None,38:'LCD_DC',39:None,40:'I2S_BCLK',41:'I2S_LRCLK',42:'I2S_DATA',44:'UART_RX',43:'UART_TX',2:'I2C_SCL',1:'I2C_SDA'}
 gpio_by_pad=[None,None,None,4,5,6,7,15,16,17,18,8,19,20,3,46,9,10,11,12,13,14,21,47,48,45,0,35,36,37,38,39,40,41,42,44,43,2,1,None]
 pins={str(i):gp.get(g) for i,g in enumerate(gpio_by_pad,1)};pins.update({'1':'GND','2':'3V2','3':'MCU_EN','40':'GND','41':'GND'})
 add('U1','ESP32-S3-WROOM-1-N16R8','RF_Module:ESP32-S3-WROOM-1',[32.5,15.75],pins,[18,25.5,3.1],[3.8,6.8],'mcu','mcu')
 # USB500 mode EN1=VBUS EN2=GND; 249mA nominal charge. TMR NC selects default timers.
 add('U2','BQ24074RGTR','Package_DFN_QFN:VQFN-16-1EP_3x3mm_P0.5mm_EP1.6x1.6mm',[47,42],{1:'CELL_NTC',2:'BAT',3:'BAT',4:'GND',5:'GND',6:'VBUS',7:None,8:'GND',9:None,10:'SYS',11:'SYS',12:'CHG_ILIM',13:'VBUS',14:None,15:'CHG_ITERM',16:'CHG_ISET',17:'GND'},[3,3,.9],[1.5,3],'power','charger')
 r('R1','1.78k',[43,39],'CHG_ILIM','GND','power');r('R2','3.57k',[40.5,36.5] if variant=='mini' else [43,46],'CHG_ISET','GND','power');r('R3','3.01k',[43,45],'CHG_ITERM','GND','power')
 c('C1','10u',[49,37],'VBUS');c('C2','10u',[51,40],'SYS');c('C3','10u',[42,42] if variant=='mini' else [55,41.5],'BAT');parts[-1]['angle']=180 if variant=='mini' else 0
 add('U3','TPS63020DSJR','Compact:TPS63020_DSJ',[52,45],{1:'VINA',2:'GND',3:'REG_FB',4:'3V2',5:'3V2',6:'SW_L2',7:'SW_L2',8:'SW_L1',9:'SW_L1',10:'SYS',11:'SYS',12:'PWR_EN',13:'SYS',14:None,15:'GND'},[3,4,1],[2.2,4.5],'power','regulator')
 add('L1','XFL4020-152MEC','Inductor_SMD:L_Coilcraft_XxL4020',[52,51],{1:'SW_L1',2:'SW_L2'},[4,4,2.1],[.9,1.8],'power','https://www.coilcraft.com/en-us/products/power/shielded-inductors/molded-inductor/xfl/xfl4020/',angle=180)
 for i,xy in enumerate([[47,46],[43.5,48.5],[43.5,51.5]],4):
  c('C'+str(i),'22u',xy,'3V2');parts[-1]['angle']=180
 r('R45','1M',[47,49],'3V2','REG_FB','power');r('R46','187k',[47,52],'REG_FB','GND','power')
 c('C7','10u',[57,44],'SYS');c('C8','100n',[49.45,42.75],'VINA');parts[-1]['angle']=270;r('R4','100k',[47,58],'PWR_EN','GND','power')
 add('SW9','JS102011SAQN','Button_Switch_SMD:SW_SPDT_CK_JS102011SAQN',[5,45],{1:'SYS',2:'PWR_EN',3:'GND'},[9,5.6,3.5],[.5,1.5],'power','https://www.ckswitches.com/media/1422/js.pdf',angle=270)
 # Low quiescent 1.8V rail for codec core only.
 add('U4','TLV75518PDBVR','Package_TO_SOT_SMD:SOT-23-5',[15,35],{1:'3V2',2:'GND',3:'3V2',4:None,5:'1V8'},[2.9,2.8,1.45],[.2,.7],'audio','ldo')
 c('C9','1u',[11,35],'3V2','GND','audio');c('C10','1u',[19,35],'1V8','GND','audio')
 cp={1:'GND',2:'3V2',3:'1V8',4:None,5:'I2S_DATA',6:'I2S_LRCLK',7:'I2S_BCLK',8:'GND',9:'I2C_SDA',10:'I2C_SCL',11:'MICDET',12:'MICBIAS',13:None,14:None,15:None,16:'GND',17:'3V2',18:'GND',19:None,20:'GND',21:'3V2',22:None,23:None,24:'3V2',25:'GND',26:None,27:'HPL',28:'3V2',29:'GND',30:'HPR',31:'IO4',32:'CODEC_IRQ',33:'GND'}
 add('U5','TLV320DAC3100IRHBR','Package_DFN_QFN:Texas_RHB0032E_VQFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm',[25,43],cp,[5,5,1],[2,4],'audio','codec')
 for i,(xy,rail) in enumerate([([21,38],'1V8'),([25,38],'3V2'),([29,38],'3V2'),([21,48],'3V2'),([25,48],'3V2')],11):c('C'+str(i),'100n',xy,rail,'GND','audio')
 c('C16','10u',[29,48],'3V2','GND','audio');r('R5','2.2k',[32,42],'MICBIAS','MICDET','audio')
 c('C17','100u',[13,76],'HPL','HP_L','audio');c('C18','100u',[19,76],'HPR','HP_R','audio')
 add('J3','SJ-43514-SMT-TR','Compact:SJ43514',[29,91],{1:'MICDET',2:'HP_L',3:'HP_R',4:'GND'},[18,9,5.05],[.8,2],'audio','jack',angle=90)
 # Hardware latch: codec IRQ sets muted asynchronously; firmware clears only after status read.
 add('U6','SN74LVC1G74DCUR','Package_SO:VSSOP-8_2.3x2mm_P0.5mm',[35,49],{1:'GND',2:'GND',3:'LATCH_ALLOW',4:'GND',5:'MUTED',6:'IO5',7:'MUTE_PRE_N',8:'3V2'},[2.3,3.1,1.1],[.25,.7],'audio','latch')
 add('Q1','MMBT3904LT1G','Package_TO_SOT_SMD:SOT-23',[35,44],{1:'IRQ_BASE',2:'GND',3:'MUTE_PRE_N'},[2.9,2.4,1.1],[.03,.12],'audio','https://www.onsemi.com/pdf/datasheet/mmbt3904lt1-d.pdf')
 r('R6','10k',[35,39],'CODEC_IRQ','IRQ_BASE','audio');r('R7','100k',[39,39],'IRQ_BASE','GND','audio');r('R8','10k',[39,43],'3V2','MUTE_PRE_N','audio');r('R9','10k',[39,47],'3V2','IO5','audio')
 add('U7','SN74LVC1G08DBVR','Package_TO_SOT_SMD:SOT-23-5',[35,55],{1:'LATCH_ALLOW',2:'SPK_REQUEST',3:'GND',4:'SPK_GATE',5:'3V2'},[2.9,2.8,1.45],[.15,.45],'audio','gate')
 r('R10','100k',[31,54],'SPK_REQUEST','GND','audio');r('R11','10k',[35,59],'SPK_GATE','AMP_SD','audio');r('R12','20k',[39,59],'AMP_SD','GND','audio')
 add('U8','MAX98357AETE+T','Package_DFN_QFN:TQFN-16-1EP_3x3mm_P0.5mm_EP1.23x1.23mm',[34,66],{1:'I2S_DATA',2:'AMP_GAIN',3:'GND',4:'AMP_SD',5:None,6:None,7:'SYS',8:'SYS',9:'SPK_P',10:'SPK_N',11:'GND',12:None,13:None,14:'I2S_LRCLK',15:'GND',16:'I2S_BCLK',17:'GND'},[3,3,.8],[1.3,3],'audio','amp')
 r('R13','100k',[30,69],'AMP_GAIN','SYS','audio');c('C19','100n',[30,63],'SYS','GND','audio');c('C20','10u',[38,63],'SYS','GND','audio');c('C21','100n',[31,49],'3V2','GND','audio');c('C22','100n',[31,57],'3V2','GND','audio')
 # Speaker via soldered flexible wire; no loose spring contact acceptance assumption.
 add('J4','S2B-PH-SM4-TB','Connector_JST:JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal',[42,79],{1:'SPK_P',2:'SPK_N'},[8,6,3.7],[.15,.6],'audio','https://www.jst-mfg.com/product/pdf/eng/ePH.pdf')
 add('U9','TCA9534PWR','Package_SO:TSSOP-16_4.4x5mm_P0.65mm',[10,55],{1:'GND',2:'GND',3:'GND',4:'KEY_UP',5:'KEY_A',6:'KEY_DOWN',7:'KEY_LEFT',8:'GND',9:'KEY_RIGHT',10:'KEY_B',11:'KEY_VOL_DOWN',12:'KEY_VOL_UP',13:None,14:'I2C_SCL',15:'I2C_SDA',16:'3V2'},[5,6.4,1.2],[.7,1.6],'controls','io')
 c('C23','100n',[6,55],'3V2');r('R14','2.2k',[10,30],'3V2','I2C_SDA');r('R15','2.2k',[15,30],'3V2','I2C_SCL');r('R16','10k',[43,30],'3V2','MCU_EN');c('C24','1u',[47,30],'MCU_EN');r('R17','10k',[52,30],'3V2','BOOT_N')
 add('SW10','KMR221GLFS','Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2',[55,24],{1:'BOOT_N',2:'GND'},[4.2,2.8,1.9],[.15,.5],'service','https://www.ckswitches.com/media/1479/kmr2.pdf')
 add('SW11','KMR221GLFS','Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2',[49,24],{1:'MCU_EN',2:'GND'},[4.2,2.8,1.9],[.15,.5],'service','https://www.ckswitches.com/media/1479/kmr2.pdf')
 coords=([(15,60),(32.5,60),(50,60),(43,70),(53,70)] if variant=='mini' else [(17,57),(44,66),(17,73),(9,65),(25,65),(54,76),(40,56),(50,56)])
 keys=(['LEFT','A','RIGHT','VOL_DOWN','VOL_UP'] if variant=='mini' else ['UP','A','DOWN','LEFT','RIGHT','B','VOL_DOWN','VOL_UP'])
 for i,(xy,key) in enumerate(zip(coords,keys),1):
  add('SW'+str(i),'KMR221GLFS','Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2',xy,{1:'KEY_'+key,2:'GND'},[4.2,2.8,1.9],[.15,.5],'controls','https://www.ckswitches.com/media/1479/kmr2.pdf')
 for i,key in enumerate(['UP','A','DOWN','LEFT','RIGHT','B','VOL_DOWN','VOL_UP'],30):r('R'+str(i),'10k',[8+(i-30)*5,51],'3V2','KEY_'+key,'controls')
 # Native USB-C, USB ESD and independent CC Rd. USB connector opens at lower edge.
 add('J1','USB4105-GF-A','Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal',[51,89.7],{'A1':'GND','A4':'VBUS','A5':'CC1','A6':'USB_P','A7':'USB_N','A8':None,'A9':'VBUS','A12':'GND','B1':'GND','B4':'VBUS','B5':'CC2','B6':'USB_P','B7':'USB_N','B8':None,'B9':'VBUS','B12':'GND','S1':'GND'},[8.94,7.35,3.2],[.25,.9],'usb','https://gct.co/connector/usb4105',angle=0)
 r('R18','5.1k',[46,83],'CC1','GND','usb');r('R19','5.1k',[51,83],'CC2','GND','usb')
 add('U10','USBLC6-2SC6','Package_TO_SOT_SMD:SOT-23-6',[52,78],{1:'USB_P',2:'GND',3:'USB_N',4:'USB_N',5:'VBUS',6:'USB_P'},[2.9,2.8,1.45],[.2,.6],'usb','https://www.st.com/resource/en/datasheet/usblc6-2.pdf')
 r('R20','27',[56,76],'USB_P','USB_DP','usb');r('R21','27',[56,79],'USB_N','USB_DN','usb')
 add('J2','DM3D-SF','Connector_Card:microSD_HC_Hirose_DM3D-SF',[53,18],{1:None,2:'SD_CS',3:'SPI_MOSI',4:'3V2',5:'SPI_SCK',6:'GND',7:'SPI_MISO',8:None,9:'GND',10:'GND',11:'GND'},[14,14.5,1.85],[.7,1.8],'storage','https://www.hirose.com/product/p/CL0609-0028-0-00',angle=90)
 c('C25','100n',[45,19],'3V2');c('C26','10u',[45,15],'3V2');r('R22','10k',[45,11],'3V2','SD_CS')
 add('J5','S2B-PH-SM4-TB','Connector_JST:JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal',[8,25],{1:'BAT',2:'GND'},[8,6,3.7],[.2,.6],'power','https://www.jst-mfg.com/product/pdf/eng/ePH.pdf')
 # Cell thermistor is separate and bonded to pouch; not a dummy resistor.
 add('J6','S2B-PH-SM4-TB','Connector_JST:JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal',[7,36],{1:'CELL_NTC',2:'GND'},[8,6,3.7],[.2,.6],'power','https://www.jst-mfg.com/product/pdf/eng/ePH.pdf')
 # Debug signals solder pads avoid header height.
 for i,net in enumerate(['GND','3V2','UART_TX','UART_RX','MUTED','IO6','IO7','SYS','BAT','1V8']):
  add('TP'+str(i+1),net,'TestPoint:TestPoint_Pad_D1.0mm',[9+i*4.5,90],{1:net},[1,1,.05],[0,0],'service')
 # U6.Q also connects to GPIO6; route alias through zero-ohm resistor not net ambiguity.
 add('R23','RC0603JR-070RL','Resistor_SMD:R_0603_1608Metric',[38,52],{1:'MUTED',2:'IO6'},[1.6,.8,.55],[.01,.05],'logic')
 add('D1','LTST-C190KGKT','LED_SMD:LED_0603_1608Metric',[10,11],{1:'LED_K',2:'LED_STATUS'},[1.6,.8,.8],[.03,.15],'controls','https://optoelectronics.liteon.com/upload/download/DS22-2000-0266/LTST-C190KGKT.pdf')
 r('R24','1k',[15,11],'LED_K','GND')
 # External module harness has literal mainboard pin order, flying leads to module silkscreen.
 if variant=='mini':
  add('J7','BM07B-SRSS-TB','Connector_JST:JST_SH_BM07B-SRSS-TB_1x07-1MP_P1.00mm_Vertical',[16,41],{1:'3V2',2:'GND',3:'SPI_SCK',4:'SPI_MOSI',5:'SPI_MISO',6:'IO8',7:'IO9'},[9,4,3],[.3,.8],'nfc','https://www.jst-mfg.com/product/pdf/eng/eSH.pdf')
  r('R25','10k',[16,45],'3V2','IO8','nfc');r('R26','10k',[11,45],'3V2','IO9','nfc')
 else:
  add('J8','FH12-18S-0.5SH(55)','Connector_FFC-FPC:Hirose_FH12-18S-0.5SH_1x18-1MP_P0.50mm_Horizontal',[37,37.5],{1:'GND',2:'IO9',3:'SPI_SCK',4:'LCD_DC',5:'LCD_CS',6:'SPI_MOSI',7:'SPI_MISO',8:'GND',9:'3V2',10:'LCD_5V',11:'LED_K1',12:'LED_K2',13:'LED_K3',14:'LED_K4',15:None,16:None,17:None,18:None},[13,5.6,2],[.5,1.1],'lcd','lcd',angle=90)
  add('U11','TPS61040DBVR','Package_TO_SOT_SMD:SOT-23-5',[15,41],{1:'LCD_SW',2:'GND',3:'LCD_FB',4:'PWR_EN',5:'SYS'},[2.9,2.8,1.45],[.6,1.4],'lcd','boost')
  add('L2','LPS4018-103MRB','Inductor_SMD:L_Coilcraft_LPS4018',[15,47],{1:'SYS',2:'LCD_SW'},[4,4,1.8],[.6,1.2],'lcd','https://www.coilcraft.com/en-us/products/power/shielded-inductors/molded-inductor/lps/lps4018/')
  add('D2','SK14-TP','Diode_SMD:D_SOD-123',[19,41],{1:'LCD_5V',2:'LCD_SW'},[3.7,1.8,1.35],[.05,.2],'lcd','https://www.mccsemi.com/pdf/Products/SK12-SK110(SOD-123).pdf')
  r('R27','1M',[10,40],'LCD_5V','LCD_FB','lcd');r('R28','332k',[10,43],'LCD_FB','GND','lcd');c('C27','10u',[20,45],'LCD_5V','GND','lcd');c('C28','10u',[11,47],'SYS','GND','lcd')
  add('Q2','AO3400A','Package_TO_SOT_SMD:SOT-23',[42,35],{1:'LCD_PWM',2:'GND',3:'LCD_SINK'},[2.9,2.4,1.1],[.05,.2],'lcd','https://www.aosmd.com/sites/default/files/res/data_sheets/AO3400A.pdf')
  r('R29','100',[42,32],'IO8','LCD_PWM','lcd');r('R38','100k',[42,37],'LCD_PWM','GND','lcd')
  for i in range(4):r('R'+str(40+i),'120',[30+i*4,30],'LED_K'+str(i+1),'LCD_SINK','lcd')
 c('C29','10u',[20.5,15],'3V2');parts[-1]['angle']=180;c('C30','100n',[21,11.75],'3V2');parts[-1]['angle']=180
 # Precision divider and forced PWM keep the panel rail below its3.3V limit.
 for item in parts:
  if item['ref']=='R45':item['mpn']='RT0603BRD071ML';item['cost_eur']=[.08,.3]
  if item['ref']=='R46':item['mpn']='RT0603BRD07187KL';item['cost_eur']=[.08,.3]
 # Keep unused MCU GPIOs truly NC, not test nets without defined function.
 used={net for p in parts if p['ref']!='U1' for net in p['pins'].values() if net}
 for pin,net in pins.items():
  if net and (net.startswith('IO') or net.startswith('LCD_')) and net not in used:parts[0]['pins'][pin]=None
 return parts

def write():
 OUT.mkdir(exist_ok=True)
 for v in ['mini','explore']:
  d={'variant':v,'status':'engineering_prototype_not_release','case':[65 if v=='mini' else 67,95 if v=='mini' else 100,22 if v=='mini' else 24],'pcb':{'outline':[2.5,9,60,83],'thickness':1.2,'z':10.5,'holes':[[6,56],[59,56],[6,88],[59,88]]},'parts':design(v),'sources':SOURCES}
  (OUT/(v+'.json')).write_text(json.dumps(d,indent=2)+'\n')
if __name__=='__main__':write()
