import machine
import time
import pcf8574
import utime

# Pin d
OE = machine.Pin(17, machine.Pin.OUT)
LE_U7 = machine.Pin(27, machine.Pin.OUT)
LE_U8 = machine.Pin(14, machine.Pin.OUT)
OE_U9 = machine.Pin(13, machine.Pin.OUT)
OE_U10 = machine.Pin(12, machine.Pin.OUT)
S0 = machine.Pin(15, machine.Pin.OUT)
S1 = machine.Pin(2, machine.Pin.OUT)
S2 = machine.Pin(4, machine.Pin.OUT)
S3 = machine.Pin(16, machine.Pin.OUT)


DI0 = machine.Pin(26, machine.Pin.IN)
DI1 = machine.Pin(25, machine.Pin.IN)
DI2 = machine.Pin(33, machine.Pin.IN)
DI3 = machine.Pin(32, machine.Pin.IN)
DI4 = machine.Pin(35, machine.Pin.IN)
DI5 = machine.Pin(34, machine.Pin.IN)
DI6 = machine.Pin(39, machine.Pin.IN)
DI7 = machine.Pin(36, machine.Pin.IN)

sdaPIN=machine.Pin(21)
sclPIN=machine.Pin(22)

cs_pin = machine.Pin(5, machine.Pin.OUT)
# clk_pin = machine.Pin(18, machine.Pin.OUT)
# miso_pin = machine.Pin(19, machine.Pin.IN)
# mosi_pin = machine.Pin(23, machine.Pin.OUT)

PCF8574_address = 0x20
current_register_h =0b000000000
current_register_l =0b000000000

# Create instance
i2c= machine.SoftI2C(sclPIN, sdaPIN)
pcf = pcf8574.PCF8574(i2c, PCF8574_address)
# spi = machine.SPI(1, baudrate=100000, polarity=0, phase=0, sck=clk_pin, mosi=None, miso=miso_pin)
# Define SPI bus pins
spi = machine.SPI(2, baudrate=1000000, polarity=0, phase=0)

#  funct
def init_Out():
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
    if val:
        value = 1
    else:
        value = 0
    
    
    if DO > 7:
       DO = DO-8 
       LE_U7.off()
       LE_U8.on()
       out_register =(current_register_h & ~(1 << DO)) | (value << DO)
       pcf.port = out_register
       current_register_h = out_register
       LE_U8.off()
    else :
       LE_U7.on()
       LE_U8.off()
       out_register =(current_register_l & ~(1 << DO)) | (value << DO)
       pcf.port = out_register
       current_register_l = out_register
       LE_U7.off()
    
    return [current_register_h,current_register_l ]


def Read_DI(DI):
    if DI > 7:
        OE_U9.on()
        OE_U10.off()
        DI_value = DI0.value()
        pass
    else:
        OE_U9.off()
        OE_U10.on()
        if DI == 0:
            DI_value = DI0.value()
            pass
        elif DI == 1:
            DI_value = DI1.value()
            pass
        elif DI == 2:
            DI_value = DI2.value()
            pass
        elif DI == 3:
            DI_value = DI3.value()
            pass
        elif DI == 4:
            DI_value = DI4.value()
            pass
        elif DI == 5:
            DI_value = DI5.value()
            pass
        elif DI == 6:
            DI_value = DI6.value()
            pass
        elif DI == 7:
            DI_value = DI7.value()
            pass
        else :
            pass
    return DI_value


def set_adc_channel(ad_channel):
    if ad_channel== 0:
        S0.off()
        S1.off()
        S2.off()
        S3.off()
    elif ad_channel== 2:
        S0.off()
        S1.on()
        S2.off()
        S3.off()
    elif ad_channel== 3:
        S0.on()
        S1.on()
        S2.off()
        S3.off()
    elif ad_channel== 5:
        S0.on()
        S1.off()
        S2.on()
        S3.off()
    elif ad_channel== 7:
        S0.on()
        S1.on()
        S2.on()
        S3.off()
    elif ad_channel== 10:
        S0.off()
        S1.on()
        S2.off()
        S3.on()
    else:
        pass


# Read function for MCP3201 ADC
def read_adc(channel):
    # Select MCP3201 ADC
    cs_pin.value(0)
    
    # Read the 12-bit ADC value
    data=spi.read(2)
    
    # Deselect MCP3201 ADC
    cs_pin.value(1)
    
    msb = data[0]
    lsb = data[1]
    adc_value = ((msb << 7) | (lsb >> 1)) & 0xfff

    return adc_value
    
