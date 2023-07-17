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

# system packages
import time
import machine
import json
import utime
import pcf8574
import autoclave

import gc
gc.collect()



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
    
val_dict = {True: 1, False: 0}
def my_coil_set_cb(reg_type, address, val):
    autoclave.S1.value(val_dict[val[0]])
    print('Custom callback, called on setting {} at {} to: {}'.
          format(reg_type, address, val))
   
   
# mio
       
    
  

def my_coil_get_cb(reg_type, address, val):
    print('Custom callback, called on getting {} at {}, currently: {}'.
          format(reg_type, address, val))


def my_discrete_inputs_register_get_cb(reg_type, address, val):
    dict_rd = {0: False, 1:True} 
    val = autoclave.read_DI(address)
     
    client.set_ist(address=address, value=dict_rd[val])
    print('Custom callback, called on getting {} at {}, currently: {}'.
          format(reg_type, address, val))

def my_inputs_register_get_cb(reg_type, address, val):
    # usage of global isn't great, but okay for an example
    global client
    
    print('Custom callback, called on getting {} at {}, currently: {}'.
          format(reg_type, address, val))

    # any operation should be as short as possible to avoid response timeouts
    new_val = val[0] + 1

    # It would be also possible to read the latest ADC value at this time
    # adc = machine.ADC(12)     # check MicroPython port specific syntax
    # new_val = adc.read()

    client.set_ireg(address=address, value=new_val)
    print('Incremented current value by +1 before sending response')


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
register_definitions['COILS']['Door Ring']['off_set_cb'] = my_coil_set_cb

# register_definitions['COILS']['Door Ring']['on_get_cb'] = my_coil_get_cb

# discrete inputs and input registers support only get callbacks as they can't
# be set externally
# register_definitions['ISTS']['EXAMPLE_ISTS']['on_get_cb'] = \
#     my_discrete_inputs_register_get_cb
register_definitions['ISTS']['Door Close']['on_get_cb'] = \
      my_discrete_inputs_register_get_cb

register_definitions['ISTS']['Ring Open']['on_get_cb'] = \
      my_discrete_inputs_register_get_cb
# register_definitions['ISTS']['Ring Close']['on_get_cb'] = \
#     my_discrete_inputs_register_get_cb


register_definitions['IREGS']['EXAMPLE_IREG']['on_get_cb'] = \
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