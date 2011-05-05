import scipy
import numpy
import Gnuplot

plt = Gnuplot.Gnuplot()

df = './Data/no_mask_dosage.dat'

data = open(df, 'r').readlines()

x = []
y = []

for line in data:
    l = line.split()
    if len(l) == 2:
        x.append(float(l[0]))
        y.append(float(l[1]))

x = numpy.array(x)
y = numpy.array(y)
xpts = numpy.unique(x)

plots = []
for i in xpts:
    bm = scipy.where( x==i)
    plots.append(Gnuplot.Data(y[bm], with_='lines'))
    print i
    plt.plot(plots[-1])
    raw_input()

apply(plt.plot, plots)

