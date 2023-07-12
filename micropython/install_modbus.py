import machine
import network
import time
import mip
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect('LADETEC', 'Tech1234')
time.sleep(1)
print('Device connected to network: {}'.format(station.isconnected()))
mip.install('github:brainelectronics/micropython-modbus')
print('Installation completed')
machine.soft_reset()