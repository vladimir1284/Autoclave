import machine
import time
import pcf8574
import utime

# Pin d
# OE = machine.Pin(17, machine.Pin.OUT)
# LE_U7 = machine.Pin(27, machine.Pin.OUT)
# LE_U8 = machine.Pin(14, machine.Pin.OUT)
# OE_U9 = machine.Pin(13, machine.Pin.OUT)
# OE_U10 = machine.Pin(12, machine.Pin.OUT)
S0 = machine.Pin(15, machine.Pin.OUT)
S1 = machine.Pin(2, machine.Pin.OUT)
S2 = machine.Pin(4, machine.Pin.OUT)
S3 = machine.Pin(16, machine.Pin.OUT)


DI0 = machine.Pin(27, machine.Pin.IN)
DI1 = machine.Pin(26, machine.Pin.IN)
DI2 = machine.Pin(25, machine.Pin.IN)
DI3 = machine.Pin(33, machine.Pin.IN)
DI4 = machine.Pin(32, machine.Pin.IN)
DI5 = machine.Pin(35, machine.Pin.IN)
DI6 = machine.Pin(34, machine.Pin.IN)
DI7 = machine.Pin(39, machine.Pin.IN)
DI8 = machine.Pin(36, machine.Pin.IN)

sdaPIN=machine.Pin(21)
sclPIN=machine.Pin(22)


PCF8574_1address = 0x20
PCF8574_2address = 0x21
current_register_h =0b000000000
current_register_l =0b000000000




# Create instance
i2c= machine.SoftI2C(sclPIN, sdaPIN)
# pcf = pcf8574.PCF8574(i2c, PCF8574_1address)

# spi = machine.SPI(1, baudrate=100000, polarity=0, phase=0, sck=clk_pin, mosi=None, miso=miso_pin)
# Define SPI bus pins
spi = machine.SPI(2, baudrate=1000000, polarity=0, phase=0)

#  funct
def init_Out():
    current_register_h =0b000000000
    current_register_l =0b000000000
    LE_U7.on()
    LE_U8.off()
    OE.off()
    pcf.port = current_register_l
    utime.sleep_ms(500)
    LE_U7.off()
    LE_U8.on()
    pcf.port = current_register_h
    utime.sleep_ms(500)
    OE_U10.on()
    utime.sleep_ms(500)
    OE_U9.on()


def write_DO (DO, val):
    global current_register_l
    global current_register_h
#     offset_DO = 100
#     DO = DO-offset_DO
     
    if DO > 7:
       DO = DO-8 
       LE_U7.off()
       LE_U8.on()
       out_register =(current_register_h & ~(1 << DO)) | (val << DO)
       pcf.port = out_register
       current_register_h = out_register
#        LE_U8.off()
    else :
       LE_U7.on()
       LE_U8.off()
       out_register =(current_register_l & ~(1 << DO)) | (val << DO)
       pcf.port = out_register
       current_register_l = out_register
#        LE_U7.off()
  #      print(DO,val)
    return [current_register_h,current_register_l ]


def read_DI(DI):
    offset_DI = 100
    DI = DI-offset_DI
    if DI > 7:
        S1.on()
        utime.sleep_ms(10)
        S1.off()
        DI_value = DI0.value()
        
    elif 0 <= DI <= 7:
        S1.on()
        utime.sleep_ms(10)
        S1.off()
        DI_value = globals()[f"DI{DI}"].value()
       
       
    else:
        DI_value = None
        
    return DI_value

def read_PCF8574(address):
     
     S2.off()
     utime.sleep_ms(10)
   
     S2.on()
#      pcf= pcf8574.PCF8574(i2c,address)
     value = i2c.readfrom(address, 1)
#      value = pcf.port 
     return value

# Map channel numbers to corresponding configuration values
channel_config = {
    0: (False, False, False, False),
    1: (False, False, False, True),
    2: (False, False, True, False),
    3: (False, False, True, True),
    4: (False, True, False , False),
    5: (False, True, False, True),
    6: (False, True, True, False),
    7: (False, True, True, True),
    8: (True, False, False, False),
    9: (True, False, False, True),
    10: (True, False, True, False)
}


# Read function for MCP3201 ADC
def read_adc( ad_channel):
    offset_AI = 200
    ad_channel = ad_channel-offset_AI
    if ad_channel in channel_config:
        # Get the configuration values for the specified channel
        s3, s2, s1, s0 = channel_config[ad_channel]
        # Set the pin values accordingly
        S0.value(s0) 
        S1.value(s1)
        S2.value(s2)
        S3.value(s3)
    else:
        # Channel not found in the configuration map
        pass

    # Select MCP3201 ADC
    cs_pin.value(0)
#     print(ad_channel)
    # Read the 12-bit ADC value
    data=spi.read(2)
    
    # Deselect MCP3201 ADC
    cs_pin.value(1)
    
    msb = data[0]
    lsb = data[1]
    adc_value = ((msb << 7) | (lsb >> 1)) & 0xfff

    return adc_value
    