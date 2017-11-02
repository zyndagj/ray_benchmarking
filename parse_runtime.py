#!/usr/bin/env python

from glob import glob
import re

reHours = re.compile(r"(\d+) hours")
reMinutes = re.compile(r"(\d+) minutes")
reSeconds = re.compile(r"(\d+) seconds")

outDirs = glob("out*-r[0-9]")
uPrefix = set([ d[:-3] for d in outDirs ])

def getInt(s, regex):
	m = regex.search(s)
	if m:
		return int(m.group(1))
	else:
		return 0

for prefix in uPrefix:
	oStr = prefix
	for ET in glob(prefix+"*/ElapsedTime.txt"):
		lastLine = totalTime = open(ET,'r').readlines()[-1]
		if 'Computing neighbourhoods' in lastLine:
			totalTime = lastLine.split('\t')[3]
			h = getInt(totalTime, reHours)
			m = getInt(totalTime, reMinutes)
			s = getInt(totalTime, reSeconds)
			ts = h*60*60+m*60+s
			oStr += "\t%i"%(ts,)
	print oStr
