import scipy
from scipy import interpolate
from scipy import integrate
import numpy
import csv
import matplotlib.pyplot as plt
import Gnuplot

def find_edge(x, profile, **kwargs):
    spline = scipy.interpolate.splrep(x, profile)
    deriv = scipy.interpolate.splev(x, spline, der = 1.0)
    bm = scipy.where( deriv > 0.5)
    if (len(bm[0]) > 0):
        order = numpy.argsort(x[bm])
        if 'plt' in kwargs:
            kwargs["plt"].plot(Gnuplot.Data(x, profile, with_='lines'), Gnuplot.Data(x, deriv, with_='lines'))
            raw_input()
        return bm[order[0]][0]
    else:
        return 0

gplt= Gnuplot.Gnuplot()

data_dir = '/home/deen/Data/Instrumentation/Exposure_System/Intensity_Distribution/'

df = 'no_mask_dosage_02.dat'
profile_out = 'slit_width_profile.dat'
profile_plot = 'slit_width_profile.ps'

data = open(data_dir+df, 'r').read().split('\n')

rpm = 100000   # rpm  10000 = 1"
speed = rpm/(10000.0*60.0) #  inches per second

x = []
t = []
z = []

for line in data:
    if len(line) > 0:
        l = line.split()
        x.append(float(l[0]))
        t.append(float(l[1]))
        z.append(float(l[2]))

x = numpy.array(x)
t = numpy.array(t)*speed
z = numpy.array(z)

xpts = numpy.unique(x)

dosage = []

for i in xpts:
    bm = scipy.where( x == i)[0]
    a = numpy.array(t[bm]).view(numpy.recarray)
    duplicates = numpy.core.records.find_duplicate(a)
    for dup in duplicates:
        dup_bm = scipy.where( (x==i) & (t == dup))[0]
        x = numpy.delete(x, dup_bm[-1])
        t = numpy.delete(t, dup_bm[-1])
        z = numpy.delete(z, dup_bm[-1])
        bm = scipy.where (x == i)

    dosage.append(scipy.integrate.simps(z[bm], t[bm]))

max_dose = max(dosage)*0.5
width = []
dosage = []

for i in xpts:
    bm = scipy.where( x == i)[0]
    scan = scipy.interpolate.interp1d(t[bm], z[bm])
    new_time = numpy.arange(min(t[bm]), max(t[bm]), step = 0.001)
    new_scan = scan(new_time)
    edge = find_edge(new_time, new_scan)
    print edge, new_time[edge]
    s = Gnuplot.Data(new_time, new_scan)
    limit = edge +1
    while ( ( (scipy.integrate.simps(new_scan[edge:limit], new_time[edge:limit]) - max_dose) < 0) & (limit<len(new_scan)-1) ):
        limit += 1
    width.append(new_time[limit]-new_time[edge])
    dosage.append(scipy.integrate.simps(new_scan[edge:limit], new_time[edge:limit]))
    print new_time[limit]
    #gplt.plot(s)
    #raw_input()

outfile = open('./Data/'+profile_out, 'w')
outwriter = csv.writer(outfile, delimiter = ',', quoting = csv.QUOTE_MINIMAL)

for dat in zip(xpts, width, dosage):
    outwriter.writerow(dat)

outfile.close()

fig_width_pt = 246.0
fig_width = 7.0  # inches
inches_per_pt = 1.0/72.27
pts_per_inch = 72.27
golden_mean = (numpy.sqrt(5)-1.0)/2.0
fig_height = fig_width*golden_mean
fig_size = [fig_width, fig_height]
params = {'backend' : 'ps',
          'axes.labelsize' : 12,
          'text.fontsize' : 12,
          'legend.fontsize' : 12,
          'xtick.labelsize' : 10,
          'ytick.labelsize' : 10,
          'text.usetex' : True,
          'figure.figsize' : fig_size}

plt.rcParams.update(params)

fig = plt.figure(0)
plt.clf()

plt.plot(xpts, width)
plt.title('Slit Profile')
plt.xlabel(r'Distance along slit (inches)')
plt.ylabel(r'Slit Width (inches)')

plt.savefig('./plots/slit_profile.eps')

fig = plt.figure(1)
plt.clf()

plt.plot(xpts, dosage)
plt.ylim(numpy.median(dosage)*1.05, numpy.median(dosage)*0.95)
plt.title('Dosage Variations along slit')
plt.xlabel(r'Distance along slit (inches)')
plt.ylabel(r'Integrated Dose')

plt.savefig('./plots/dosage.eps')
