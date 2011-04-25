import serial
import time
import numpy
import threading
import socket
import sys
import Gnuplot

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

plt = Gnuplot.Gnuplot()

configuration_text = open('exposure_control_config.txt', 'r').readlines()
parameters = dict()
for line in configuration_text:
    if ((line[0] != '#') & (line[0] != '\n') ):
        l = line.split()
        try:
            parameters[l[0].upper()] = float(l[2])
            print 'Added float ', parameters[l[0].upper()], ' as entry for key ', l[0].upper()
        except:
            if line.find("\"") == -1:
               parameters[l[0].upper()] = l[2]
               print 'Added text variable ', parameters[l[0].upper()], ' as entry for key ', l[0].upper()
            else:
               parameters[l[0].upper()] = line[line.find("\"")+1:line.rfind("\"")]
               print 'Added new text variable ', parameters[l[0].upper()], ' as entry for key ', l[0].upper()

UV = voltageReader(parameters)
time.sleep(1)

t1 = time.time()
print "Serial Communication Program"
print " cross your fingers"
timeout = 0.25

outputdatafile = parameters["DATA_DIR"]+parameters["FILENAME"]

#Set up the Smart-Motor interface
smi = serial.Serial(parameters["SMI_COM_PORT"], bytesize=parameters["SMI_BYTESIZE"], parity=parameters["SMI_PARITY"],stopbits=parameters["SMI_STOPBITS"], baudrate = parameters["SMI_BAUDRATE"])

smi.write('ECHO_OFF\n')
smi.write('SADR1\n')
smi.write('ZS\n')
smi.write('LIMH\n')
smi.write('PID4\n')

junk = smi.read(smi.inWaiting())
#Send motor home

smi.write('MV\n')
smi.write('A=40\n')
smi.write('V=200000\n')
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

smi.write('MP\nV=200000\nP=-100000\n')
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
ystart = -0.5
ystop = 2.0
start_pos = spi*ystart
end_pos = spi*ystop

# x direction is parallel to slit
xstart = 2
xstop = 8.5
xstep = 0.5

nptsx = int((xstop-xstart)/xstep)+1

m = []

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
      readings = UV.readVoltage().split('\r\n')
      intensity = []
      for reading in readings:
          try:
              intensity.append(float(reading))
          except:
              print 'Oops'
      m.append(intensity)
      plt.plot(Gnuplot.Data(intensity, with_='lines'))


smi.close()

out = open(outputdatafile, 'a')
xcoords = numpy.arange(0, nptsx)*xstep + xstart
passes = []
for p, x in zip(m, xcoords):
   profile = []
   for reading in p:
      out.write(str(x)+'  '+str(reading)+'\n')
   passes.append(Gnuplot.Data(profile, with_='lines'))

apply(plt.plot, passes)
out.close()

