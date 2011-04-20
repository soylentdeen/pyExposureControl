import serial
import time
import numpy
import threading
import socket
import sys
import Gnuplot
#import pylab
#import scipy
#from scipy.interpolate import splprep, splev

class voltageReader( object ):
   def __init__(self, parameters):
      self.host = parameters['UV_HOST']
      self.port = int(parameters['UV_PORT'])
      self.sock = None

      for res in socket.getaddrinfo(self.host, self.port, socket.AF_UNSPEC, socket.SOCK_STREAM):
         af, socktype, proto, canonname, sa = res
         try:
            self.sock = socket.socket(af, socktype, proto)
         except socket.error, msg:
            self.sock = None
            continue
         try:
            self.sock.connect(sa)
         except socket.error, msg:
            self.sock.close()
            self.sock = None
            continue
         break
      if self.sock is None:
         print 'Error! Could not open the socket for the motor control!'
         sys.exit(1)
      self.sock.settimeout(0.5)

   def startMeasurement(self):
      self.sock.send('START\r\n')

   def stopMeasurement(self):
      self.sock.send('STOP\r\n')
      
   def readVoltage(self):
      try:
         retval = self.sock.recv(1024000)
      except:
         retval = None
      return retval

   def close(self):
      self.sock.close()

class measurement:
   x = 0.0
   y = 0.0
   z = 0.0
   dz = 0.0

parameters = {'UV_HOST':'127.0.0.1', 'UV_PORT':2526}

UV = voltageReader(parameters)
time.sleep(1)
'''
UV.startMeasurement()
time.sleep(5)
try:
   a = UV.readVoltage()
except:
   a = 'None'
print a
time.sleep(10)
UV.stopMeasurement()
try:
   b = UV.readVoltage()
except:
   b = 'None'
UV.close()
print asdf
'''
t1 = time.time()
print "Serial Communication Program"
print " cross your fingers"
timeout = 0.25
baudrate = 9600
NEWLINE_CONVERSION_MAP = ('\n', '\r', '\r\n')

outputdatafile = 'baffle_test.dat'

#Set up the Smart-Motor interface
smi = serial.Serial(4, bytesize=8, parity='N', stopbits=1, baudrate=9600)

smi.write('ECHO_OFF\n')
smi.write('SADR1\n')
smi.write('ZS\n')
smi.write('LIMH\n')
smi.write('PID4\n')

junk = smi.read(smi.inWaiting())
#Send motor home

smi.write('MV\n')
smi.write('A=40\n')
smi.write('V=400000\n')
smi.write('G\n')

left_limit_switch = 0
right_limit_switch = 0
while ((left_limit_switch + right_limit_switch) == 0.0):
   smi.write('RBl\nRBr\nRP\nZS\n')
   time.sleep(0.5)
   readings = smi.read(smi.inWaiting()).split('\r')
   left_limit_switch = float(readings[0])
   right_limit_switch = float(readings[1])
   position = float(readings[2])


smi.write('X\nO=0\nZS\n')

smi.write('MP\nV=400000\nP=-100000\n')
smi.write('G\n')

position = 0
while( abs(position- (-100000)) > 2):
   smi.write('RP\n')
   time.sleep(1.0)
   readings = smi.read(smi.inWaiting()).split('\r')
   position = float(readings[0])
   print position

#set zero point here
smi.write('O=0\nZS\n')

spi = 10000.0  # steps per inch

t = numpy.zeros(0, float)

# y direction is perpendicular to slit
'''
ystart = float(raw_input('Enter Y-starting position: '))
ystop = float(raw_input('Enter Y-stopping position: '))
ystep = float(raw_input('Enter Y-step size: '))
'''
ystart = -1.0
ystop = 3.0
start_pos = spi*ystart
end_pos = spi*ystop
#ystep = 0.1

# x direction is parallel to slit
'''
xstart = float(raw_input('Enter X-starting position: '))
xstop = float(raw_input('Enter X-stopping position: '))
xstep = float(raw_input('Enter X-step size: '))
'''
xstart = 2
xstop = 2.1
xstep = 0.1

#nptsy = int((ystop-ystart)/ystep)+1
nptsx = int((xstop-xstart)/xstep)+1

m = []
#meas = numpy.zeros([nptsx, nptsy])

for x in range(0, nptsx):
   x_coord = x*xstep + xstart
   print x_coord
   choice = raw_input('(C)ontinue, (S)kip, (Q)uit? :')
   if choice == 'Q':
      break
   if choice != 'S':
      smi.write('RP\n')
      time.sleep(0.2)
      curr_pos = int(smi.read(smi.inWaiting()).split('\r')[0])
      smi.write('P='+str(int(start_pos))+'\nG\n')
      while( (abs(curr_pos-start_pos) > 5) ):
         smi.write('RP\n')
         time.sleep(0.2)
         curr_pos = int(smi.read(smi.inWaiting()).split('\r')[0])
      smi.write('RP\n')
      time.sleep(0.2)
      curr_pos = int(smi.read(smi.inWaiting()).split('\r')[0])
      UV.startMeasurement()
      smi.write('P='+str(int(end_pos))+'\nG\n')
      while( abs(curr_pos-end_pos) > 5):
         smi.write('RP\n')
         time.sleep(0.2)
         curr_pos = int(smi.read(smi.inWaiting()).split('\r')[0])
      UV.stopMeasurement()
      m.append(UV.readVoltage().split('\r\n'))


smi.close()

plt = Gnuplot.Gnuplot()

out = open(outputdatafile, 'w')
xcoords = numpy.arange(0, nptsx)*xstep + xstart
passes = []
for p, x in zip(m, xcoords):
   profile = []
   for reading in p:
      try:
         profile.append(float(reading))
         out.write(str(x)+'  '+str(profile[-1])+'\n')
      except:
         print 'Oops'
   passes.append(Gnuplot.Data(profile, with_='lines'))

apply(plt.plot, passes)
out.close()

print asdf
f = open(outputdatafile, 'a')

for x in range(0, nptsx):
   if meas[x][0] != 0.0:
      x_coord = x*xstep+xstart
      f.write(str(x_coord))
      f.write('\n')
      for y in range(0, nptsy):
         f.write(str(meas[x][y]))
         f.write('    ')
      f.write('\n')

f.close()

