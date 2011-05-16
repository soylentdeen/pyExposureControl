import scipy
import scipy.integrate
import numpy
import Gnuplot

plt = Gnuplot.Gnuplot()

#df = '/home/deen/Data/Instrumentation/Exposure_System/Intensity_Distribution/baffle_test_04262011.dat'
#of_name = ['weisong_raw.ps', 'weisong_int.ps']
df = '/home/deen/Data/Instrumentation/Exposure_System/Intensity_Distribution/no_mask_dosage_02.dat'
plot_name = ['no_mask_02_raw.ps', 'no_mask_02_int.ps']
of_name = 'no_mask_02_processed.dat'
#df = '/home/deen/Data/Instrumentation/Exposure_System/Intensity_Distribution/repeatability.dat'
#plot_name = ['repeatability_raw.ps', 'repeatability_int.ps']
#of_name = 'repeatability_processed.dat'

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
    a = numpy.array(t[bm]).view(numpy.recarray)
    duplicates = numpy.core.records.find_duplicate(a)
    for dup in duplicates:
        dup_bm = scipy.where( (x==i) & (t == dup))[0]
        x = numpy.delete(x, dup_bm[-1])
        t = numpy.delete(t, dup_bm[-1])
        y = numpy.delete(y, dup_bm[-1])
        bm = scipy.where (x == i)
        
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

out = open('./plots/'+of_name, 'w')
out_dosage = dosage/max(dosage)
for dat in zip(xpts, out_dosage):
    out.write(str(dat[0])+' '+str(dat[1])+'\n')

out.close()

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
plt('set out "./plots/'+plot_name[0]+'"')
apply(plt.plot, plots)
#raw_input()
plt('set out "./plots/'+plot_name[1]+'"')
d = Gnuplot.Data(xpts, dosage)
plt.plot(d)
plt('set out')
plt('set terminal x11')
