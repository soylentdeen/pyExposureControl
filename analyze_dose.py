import scipy
import scipy.integrate
import numpy
import Gnuplot

plt = Gnuplot.Gnuplot()

#df = '/home/deen/Data/Instrumentation/Exposure_System/Intensity_Distribution/baffle_test_04262011.dat'
#of_name = ['weisong_raw.ps', 'weisong_int.ps']
df = '/home/deen/Data/Instrumentation/Exposure_System/Intensity_Distribution/dosage.dat'
of_name = ['casey_raw.ps', 'casey_int.ps']

data = open(df, 'r').readlines()

x = []
t = []
y = []

for line in data:
    l = line.split()
    if len(l) == 2:
        x.append(float(l[0]))
        y.append(float(l[1]))
    if len(l) == 3:
        x.append(float(l[0]))
        t.append(float(l[1]))
        y.append(float(l[2]))

x = numpy.array(x)
t = numpy.array(t)
y = numpy.array(y)
dosage = []
sig = []
means = []
xpts = numpy.unique(x)

plots = []
for i in xpts:
    bm = scipy.where( x==i)
    #plots.append(Gnuplot.Data(y[bm], with_='lines'))
    #dosage.append(scipy.integrate.simps(y[bm]))
    plots.append(Gnuplot.Data(t[bm], y[bm], with_='lines'))
    dosage.append(scipy.integrate.simps(y[bm], x=t[bm]))
    sig.append(numpy.std(y[bm]))
    means.append(numpy.mean(y[bm]))
    plt.plot(plots[-1])


dosage = numpy.array(dosage)
sig = numpy.array(sig)
means = numpy.array(means)

bkgndbm = scipy.where( (xpts <= 2.1) | (xpts >= 7.8) )[0]
bkgnd = numpy.mean(means[bkgndbm])
error = numpy.mean(sig[bkgndbm])
bm = scipy.where( (xpts > 2.1) & (xpts < 7.8) )[0]

mn = numpy.mean(dosage[bm])
std = numpy.std(dosage[bm])
print "mean dose = ", mn-bkgnd
print "standard Deviation = ", std/(mn-bkgnd) *100.0, "%"
print "Background = ", bkgnd
print "Error = ", error

plots.append(Gnuplot.Data([0, 17], [bkgnd, bkgnd], with_='lines'))
plots.append(Gnuplot.Data([0, 17], [bkgnd-error, bkgnd-error], with_='lines'))
plots.append(Gnuplot.Data([0, 17], [bkgnd+error, bkgnd+error], with_='lines'))

plt('set terminal postscript')
plt('set out "'+of_name[0]+'"')
apply(plt.plot, plots)
#raw_input()
plt('set out "'+of_name[1]+'"')
d = Gnuplot.Data(xpts, dosage)
plt.plot(d)
plt('set out')
plt('set terminal x11')
