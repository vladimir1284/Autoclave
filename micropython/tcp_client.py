#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Main script

Do your stuff here, this file is similar to the loop() function on Arduino

Create a Modbus TCP client (slave) which can be requested for data or set with
specific values by a host device.

The TCP port and IP address can be choosen freely. The register definitions of
the client can be defined by the user.
"""
HARDWARE_CONNECTED = True

# system packages
import time
import json

if HARDWARE_CONNECTED:
    import autoclave
else:
    import urandom

# import modbus client classes
from umodbus.tcp import ModbusTCP

import network
# connect to a network
station = network.WLAN(network.STA_IF)
if station.active() and station.isconnected():
    station.disconnect()
    time.sleep(1)
station.active(False)
time.sleep(1)
station.active(True)
station.connect('Robert_cell', 'robert08907')
# station.connect('LADETEC', 'Tech1234')

time.sleep(1)

while True:
    print('Waiting for WiFi connection...')
    if station.isconnected():
        print('Connected to WiFi.')
        print(station.ifconfig())
        break
    time.sleep(2)

# ===============================================
# TCP Slave setup
tcp_port = 502              # port to listen to

# set IP address of the MicroPython device explicitly
# local_ip = '192.168.4.1'    # IP address
# or get it from the system after a connection to the network has been made
local_ip = station.ifconfig()[0]

# ModbusTCP can get TCP requests from a host device to provide/set data
client = ModbusTCP()
is_bound = False

# check whether client has been bound to an IP and port
is_bound = client.get_bound_status()

if not is_bound:
    client.bind(local_ip=local_ip, local_port=tcp_port)
#    mio
ncoils = 16
coils = [False]*16   
val_dict = {True: 1, False: 0}

def my_coil_set_cb(reg_type, address, val):
#     autoclave.S1.value(val_dict[val[0]])
   
#     print('Custom callback, called on setting {} at {} to: {}'.
#           format(reg_type, address, val))
  #  print(a)
   
    print('trama que entra de DO',val)
    print('address',address)
    autoclave.write_DO(address,val_dict[val[0]])
    coils[address] = val[0]
    print(coils)
    data = coils
    reversed_data=[]
    for i in range(0, len(data), 8):
        segment = data[i:i+8]
        segment = segment[::-1]  # Reverse the segment
        reversed_data += segment
    print('trama que sale', reversed_data)
    client.set_coil(0,reversed_data)
    
    
   
# mio
       
    
  

def my_coil_get_cb(reg_type, address, val):
    print('Custom callback, called on getting {} at {}, currently: {}'.
          format(reg_type, address, val))
    
def my_discrete_inputs_register_get_cb(reg_type, address, val):
    value = []
#     add = []
    DI_offset = 100
#     print(val)
#     dict_rd = {0: False, 1:True}
#     value = val
#     vorig = val
#     for i, di in enumerate(val):
#         di = autoclave.read_DI(address +i)
#         v = (dict_rd[di])
#         index= (address -  DI_offset)
#         if index > 7:
#             val[8] = v
#         else:
#             val[7-i]= v
            
#         client.set_ist(address=address, value=val)     
#     print('Custom callback, called on getting {} at {}, currently: {}'.
#             format(reg_type, address, val))
   
   
    
#       val[index+7 +i] = v
      
    if HARDWARE_CONNECTED:
        dict_rd = {0: False, 1:True}
        for i, di in enumerate(val):
            di = autoclave.read_DI(address +i)
            value.append(dict_rd[di])
             
            
    else:
        for di in val:
            value.append(urandom.getrandbits(1))
    data=value        
#     print('trama que sale DI',value)
    reversed_data=[]
    for i in range(0, len(data), 8):
        segment = data[i:i+8]
        segment = segment[::-1]  # Reverse the segment
        reversed_data += segment
   
#     print('trama que sale ', reversed_data)
            
    client.set_ist(address=address, value=reversed_data)
# #     value.reverse()
#     first_part = value[:8]
#     last_part =  value[-1]
#     first_part.reverse()
#     first_part.append(last_part)
#     print(first_part)
#     

 

def my_inputs_register_get_cb(reg_type, address, val):
    # usage of global isn't great, but okay for an example
    global client
    n= len(val)
#     print(n)
    adc_value = []
   
#     print(val)
#     dadc = autoclave.read_adc(address+5)
#     adc_value.append([dadc])
    for i, dadc in enumerate(val):
        dadc = autoclave.read_adc(address+i)
        adc_value.append(dadc)
        add= address+i
            
#     adc_value.append(new_val)
#     print(adc_value)
#     adc_value = [0, 4095, 4095, 2, 1, 4095, 4095, 4095, 3129, 4095, 4095, 4095]
#     adc_value = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110]   
#     data1=adc_value

#     n = len(adc_value)
#     fp = list(adc_value[:8])
#     lp = list(adc_value[8:])
# 
#     fp.reverse()
#     lp.reverse()
# 
#     adc_value = fp + lp
#     print(data1, adc_value)   
    # any operation should be as short as possible to avoid response timeouts
#     new_val = val[0] + 1
     
    # It would be also possible to read the latest ADC value at this time
    # adc = machine.ADC(12)     # check MicroPython port specific syntax
    # new_val = adc.read()
   
    client.set_ireg(address=address, value=adc_value)
#     print('Incremented current value by +1 before sending response')
#     print('Custom callback, called on getting {} at {}, currently: {}'.
#         format(reg_type, address, adc_value))


def reset_data_registers_cb(reg_type, address, val):
    # usage of global isn't great, but okay for an example
    global client
    global register_definitions

    print('Resetting register data to default values ...')
    client.setup_registers(registers=register_definitions)
    print('Default values restored')


# commond slave register setup, to be used with the Master example above
with open('registers.json', 'r') as file:
    register_definitions = json.load(file)


# add callbacks for different Modbus functions
# each register can have a different callback
# coils and holding register support callbacks for set and get
register_definitions['COILS']['Door Ring']['on_set_cb'] =  my_coil_set_cb
# register_definitions['COILS']['Door Ring']['on_get_cb'] = my_coil_get_cb

register_definitions['COILS']['Water to coil']['on_set_cb'] =  my_coil_set_cb
# register_definitions['COILS']['Water to coil']['on_get_cb'] =  my_coil_get_cb

register_definitions['COILS']['Cooling Drain']['on_set_cb'] =  my_coil_set_cb
# register_definitions['COILS']['Cooling Drain']['on_get_cb'] =  my_coil_get_cb

register_definitions['COILS']['Compresed air to chamber']['on_set_cb'] =  my_coil_set_cb
# register_definitions['COILS']['Compresed air to chamber']['on_get_cb'] = my_coil_get_cb

register_definitions['COILS']['ATM Air']['on_set_cb'] =  my_coil_set_cb
# register_definitions['COILS']['ATM Air']['on_get_cb'] = my_coil_get_cb

register_definitions['COILS']['Fast Exah']['on_set_cb'] =  my_coil_set_cb
# register_definitions['COILS']['Fast Exah']['on_get_cb'] = my_coil_get_cb

register_definitions['COILS']['Vacuum']['on_set_cb'] =  my_coil_set_cb
# register_definitions['COILS']['Vacuum']['on_get_cb'] = my_coil_get_cb

register_definitions['COILS']['Condence']['on_set_cb'] =  my_coil_set_cb
# register_definitions['COILS']['Condence']['on_get_cb'] = my_coil_get_cb

register_definitions['COILS']['Door Ring']['on_set_cb'] =  my_coil_set_cb
# register_definitions['COILS']['Door Ring']['on_get_cb'] = my_coil_get_cb

register_definitions['COILS']['Cool pipe Flush']['on_set_cb'] =  my_coil_set_cb
# register_definitions['COILS']['Cool pipe Flush']['on_get_cb'] = my_coil_get_cb

register_definitions['COILS']['Vacumm breaker']['on_set_cb'] =  my_coil_set_cb
# register_definitions['COILS']['Vacumm breaker']['on_get_cb'] = my_coil_get_cb

register_definitions['COILS']['Heather']['on_set_cb'] =  my_coil_set_cb
# register_definitions['COILS']['Heather']['on_get_cb'] = my_coil_get_cb

register_definitions['COILS']['Vac pump']['on_set_cb'] =  my_coil_set_cb
# register_definitions['COILS']['Vac pump']['on_get_cb'] = my_coil_get_cb

register_definitions['COILS']['Circ pump']['on_set_cb'] =  my_coil_set_cb
# register_definitions['COILS']['Vac pump']['on_get_cb'] = my_coil_get_cb

register_definitions['COILS']['Water pump']['on_set_cb'] =  my_coil_set_cb
# register_definitions['COILS']['Water pump']['on_get_cb'] = my_coil_get_cb

register_definitions['COILS']['Reserva1']['on_set_cb'] =  my_coil_set_cb
# register_definitions['COILS']['Water pump']['on_get_cb'] = my_coil_get_cb

register_definitions['COILS']['Reserva2']['on_set_cb'] =  my_coil_set_cb
# register_definitions['COILS']['Water pump']['on_get_cb'] = my_coil_get_cb



# register_definitions['COILS']['Door Ring']['on_get_cb'] = my_coil_get_cb

# discrete inputs and input registers support only get callbacks as they can't
# be set externally
# register_definitions['ISTS']['EXAMPLE_ISTS']['on_get_cb'] = \
#     my_discrete_inputs_register_get_cb
register_definitions['ISTS']['Door Close']['on_get_cb'] = \
      my_discrete_inputs_register_get_cb

register_definitions['ISTS']['Ring Open']['on_get_cb'] = \
      my_discrete_inputs_register_get_cb

register_definitions['ISTS']['Ring Close']['on_get_cb'] = \
      my_discrete_inputs_register_get_cb

register_definitions['ISTS']['Flow sw Gen Pump']['on_get_cb'] = \
      my_discrete_inputs_register_get_cb

register_definitions['ISTS']['Flow sw Var Pump']['on_get_cb'] = \
      my_discrete_inputs_register_get_cb

register_definitions['ISTS']['Ring Close2']['on_get_cb'] = \
      my_discrete_inputs_register_get_cb

register_definitions['ISTS']['Ring Close3']['on_get_cb'] = \
      my_discrete_inputs_register_get_cb

register_definitions['ISTS']['Ring Close4']['on_get_cb'] = \
      my_discrete_inputs_register_get_cb

register_definitions['ISTS']['Gasket sw']['on_get_cb'] = \
      my_discrete_inputs_register_get_cb



#     my_discrete_inputs_register_get_cb

register_definitions['IREGS']['EXAMPLE_IREG']['on_get_cb'] = \
    my_inputs_register_get_cb

register_definitions['IREGS']['Elect Low']['on_get_cb'] = \
    my_inputs_register_get_cb

register_definitions['IREGS']['Chamber Press']['on_get_cb'] = \
    my_inputs_register_get_cb

register_definitions['IREGS']['Elect Chamber']['on_get_cb'] = \
    my_inputs_register_get_cb

register_definitions['IREGS']['Chamber Temp']['on_get_cb'] = \
    my_inputs_register_get_cb


register_definitions['IREGS']['Chamber Temp2']['on_get_cb'] = \
    my_inputs_register_get_cb

register_definitions['IREGS']['Drain Temp']['on_get_cb'] = \
    my_inputs_register_get_cb




# reset all registers back to their default value with a callback
register_definitions['COILS']['RESET_REGISTER_DATA_COIL']['on_set_cb'] = \
    reset_data_registers_cb

print('Setting up hardware ...')


print('Setting up registers ...')
# use the defined values of each register type provided by register_definitions
client.setup_registers(registers=register_definitions)
# alternatively use dummy default values (True for bool regs, 999 otherwise)
# client.setup_registers(registers=register_definitions, use_default_vals=True)
print('Register setup done')

print('Serving as TCP client on {}:{}'.format(local_ip, tcp_port))





while True:
    try:
        result = client.process()
    except KeyboardInterrupt:
        print('KeyboardInterrupt, stopping TCP client...')
        break
    except Exception as e:
        print('Exception during execution: {}'.format(e))

print("Finished providing/accepting data as client")