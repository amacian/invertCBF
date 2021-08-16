from math import e
from math import log as ln

# Short script developed by Stefan Walzer on sagemath that reproduces the curves
# corresponding to the expected fraction of recovered elements
k = None
cs = None

def setK(kk):
	global k
	global cs
	k = kk
	cs = ln(2)/k

def round(ps,pf,cf):
	global cs
	qs = ps**(k-1)
	qf = pf**(k-1)
	ps = 1-e**(-k*cf*qf)
	pf = 1-e**(-k*cs*qs)
	return (ps,pf)

def getCoreDensity(cf):
	(ps,pf) = (1,1)
	for i in range(1000):
		(ps,pf) = round(ps,pf,cf)
	return ps**k

def find_threshold():
	(low,high) = (0,500)
	while(high - low > 0.0001):
		mid = (low + high)/2
		if (getCoreDensity(mid) < 0.000001):
			low = mid
		else:
			high = mid
	return low

for kk in range(3,9):
    setK(kk)
    show(line2d([(x/100,1-getCoreDensity(x/100*2**k*cs)) for x in range(100,600)]))
