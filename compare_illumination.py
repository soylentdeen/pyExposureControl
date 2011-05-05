import scipy
import scipy.integrate
import numpy
import Gnuplot

df = 'coll_intensity_map_diffuser_021511.dat'

dat = open(df, 'r').readlines()

old_xpts = []
old_ypts = []

for line in dat:
    l = line.split()
    if (len(l) == 1):
        old_xpts.append(float(l[0]))
    else:
        readings = []
        for r in l:
            readings.append(float(r))
        readings = numpy.array(readings)
        old_ypts.append(scipy.integrate.simps(readings))

new_xpts = []
new_ypts = []

dat = open('plots/no_mask_processed.dat', 'r').readlines()
for line in dat:
    l = line.split()
    new_xpts.append(float(l[0]))
    new_ypts.append(float(l[1]))

plt = Gnuplot.Gnuplot()
old_ypts = old_ypts/min(old_ypts)
old_dosage = Gnuplot.Data(old_xpts, old_ypts, with_='linespoints', title = 'Old Measurements')
new_dosage = Gnuplot.Data(new_xpts, new_ypts, with_='linespoints', title = 'New Measurements')

plt('set terminal postscript')
plt('set out "dosage_comparison.ps"')
plt.plot(old_dosage, new_dosage)
plt('set out')
plt('set terminal x11')
