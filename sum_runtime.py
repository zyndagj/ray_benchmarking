#!/usr/bin/env python

from glob import glob
import re, os

reHours = re.compile(r"(\d+) hours")
reMinutes = re.compile(r"(\d+) minutes")
reSeconds = re.compile(r"(\d+) seconds")

outDirs = glob("out*-r[0-9]")
repRe = re.compile(r'-r(\d+)')
kRe = re.compile(r'-k(\d+)-')

kSet = set([])
repSet = set([])
uPrefix = set([])

for dir in outDirs:
	repSet.add(repRe.search(dir).group(1))
	kSet.add(kRe.search(dir).group(1))
	uPrefix.add(re.sub(r'-k\d.*','',dir))

def getInt(s, regex):
	m = regex.search(s)
	if m:
		return int(m.group(1))
	else:
		return 0

for prefix in sorted(uPrefix):
	oStr = prefix
	for rep in sorted(repSet):
		total = 0
		write = True
		for k in sorted(kSet):
			dir = '%s-k%s-r%s'%(prefix,k,rep)
			ET = '%s/ElapsedTime.txt'%(dir)
			if not os.path.exists(ET):
				write = False
				break
			lastLine = totalTime = open(ET,'r').readlines()[-1]
			if not 'Computing neighbourhoods' in lastLine:
				write = False
				break
			totalTime = lastLine.split('\t')[3]
			h = getInt(totalTime, reHours)
			m = getInt(totalTime, reMinutes)
			s = getInt(totalTime, reSeconds)
			ts = h*60*60+m*60+s
			total += ts
		if write:
			oStr += "\t%i"%(total,)
	print oStr
