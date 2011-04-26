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
m = []
UV.startMeasurement()
time.sleep(10)
UV.stopMeasurement()
time.sleep(2.0)
readings = UV.readVoltage().split('\r\n')
intensity = []
t = []
for line in readings:
   reading = line.split(',')
   try:
      intensity.append(float(reading[0]))
      t.append(float(reading[1]))
   except:
      print 'Oops'
m.append(zip(t, intensity))
plt.plot(Gnuplot.Data(t, intensity, with_='lines'))


print asdf