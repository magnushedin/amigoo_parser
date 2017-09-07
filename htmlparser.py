from html.parser import HTMLParser
from html.entities import name2codepoint

import sys
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

import urllib.request
import re

def dprint(*text):
	#print(text)
	pass

class MyHTMLParser(HTMLParser):
	laps = [] # time for each parsed lap
	lap_nr = [] # order in which the laps are parsed
	save_lap = 0
	save_time = 0
	save_name = 0
	driver = ""
	nolap = 0

	def getDriverName(self):
		dprint("will return driver name: ", self.driver)
		return self.driver

	def getData(self):
		laps = []
		lap_nr = []
		for j, i in enumerate(self.lap_nr):
			laps.append(self.laps[i-1])
			lap_nr.append(j+1)
		return lap_nr.copy(), laps.copy()

	def clearParser(self):
		self.laps.clear()
		self.lap_nr.clear()
		self.save_lap = 0
		self.save_time = 0
		self.driver = ""
		self.nolap = 0

	def printlaps(self):
		for i, lap in enumerate(self.lap_nr):
			#print("lap:", i+1, " - ",self.laps[lap-1])
			pass

	def handle_starttag(self, tag, attrs):
		dprint("<", tag, ">")
		for attr in attrs:
			dprint("     attr:", attr)
			if (attr[1] == 'lap'):
				dprint("deb, will save lap: ", attr)
				self.save_lap = 1
			if (attr[0] == 'title'):
				dprint("deb, will save time: ", attr)
				self.save_time = 1

	def handle_endtag(self, tag):
		dprint("</", tag, ">")
		pass

	def handle_data(self, data):
		dprint("Data     :", data)
		if ((self.save_lap == 1) & (data != 'Lap')):
			dprint("deb, saved a lap: ", data)
			try:
				self.lap_nr.append(int(data))
				self.nolap = 0
			except:
				#print("error saving lap: ", data)
				self.nolap = 1
		if ((self.save_time == 1) & (self.nolap == 0)):
			dprint("deb, saved some time: ", data)
			try:
				self.laps.append(float(data))
			except:
				self.laps.append(float(0))
				#print("error saving time: ", data)
		if (self.save_name == 1):
			self.save_name = 0
			self.driver = data
		if (data == 'Name'):
			self.save_name = 1

		self.save_time = 0
		self.save_lap = 0

	def handle_comment(self, data):
		dprint("Comment  :", data)
		pass

	def handle_entityref(self, name):
		c = chr(name2codepoint[name])
		dprint("Named ent:", c)

	def handle_charref(self, name):
		if name.startswith('x'):
			c = chr(int(name[1:], 16))
		else:
			c = chr(int(name))
		dprint("Num ent  :", c)
		pass

	def handle_decl(self, data):
		dprint("Decl     :", data)
		pass


# what heat are we parsing?
if len(sys.argv) > 1:
	url = "http://www.amigoo.se/heat/" + sys.argv[1]
else:
	#default
	url = 'http://www.amigoo.se/heat/35291'

# get html from requested url
html = urllib.request.urlopen(url)
urls = []

htmlpage = str(html.read())

# find driver id's in the requested heat-page and store in list with heat and driver id
match = re.findall(r'openLapsWindow\(([0-9]*),([0-9]*)', htmlpage, re.I|re.M)
for i in match:
    urls.append("http://amigoo.se/lap?heatid=" + i[0] + "&participantid=" + i[1])

heatname = ""
print("Heat type:")
match = re.findall(r'Heat</td><td><a href=\"/event/1469\">([a-z,A-Z,0-9]*)', htmlpage, re.I|re.M)
for name in match:
	#print(i)
	heatname = name

cartclass = ""
matches = re.findall(r'<td class=\"class\" title=\"([a-z,A-Z,0-9]*)', htmlpage, re.I|re.M)
for match in matches:
	cartclass = match

#print("html.read()")
#print(htmlpage)

print("Fetched driver urls from -->", url , ":")
for url in urls:
	print(url)
print("")

fig, ax = plt.subplots()
plt.axis([0.5, 24, 0, 46])
fig2, ax2 =plt.subplots()
plt.axis([0.5, 24, 0, 40])

fastestlaps = []
timediff = []
timederiv = []

# open and parse each drivers own page
for url in urls:
	html = urllib.request.urlopen(url)
	parser = MyHTMLParser()
	parser.feed(str(html.read()))
	#parser.printlaps()
	lap_nr, laps = parser.getData()

	if (fastestlaps == []):
		fastestlaps = laps.copy()
		for i in (lap_nr):
			timediff.append(0)
	else:
		for i in (lap_nr):
			timediff.append(laps[i-1] - fastestlaps[i-1])

	olddiff = 0
	for i, diff in enumerate(timediff):
		timederiv.append(diff + olddiff)
		olddiff = diff + olddiff

	#print("Lap number: ", lap_nr)
	print("url: ", url)
	print("Driver name: ", parser.getDriverName())
	#print("Lap time: ", laps)
	print( '{:<12s} {:<12s} {:<12s}'.format("Laptime", "delta diff", "diff") )
	for i in lap_nr:
		print('{:<12.3f} {:<12.3f} {:<12.3f}'.format(laps[i-1], timediff[i-1], timederiv[i-1]))
	print("\n")



	ax.plot(lap_nr, laps, label=parser.getDriverName())
	ax2.plot(lap_nr, timederiv, label=parser.getDriverName())
	parser.clearParser()
	timediff = []
	timederiv = []

legend = ax.legend(shadow=True)
legend2 = ax2.legend(shadow=True)
ax.set_title(heatname + ", " + cartclass)
ax2.set_title(heatname + ", " + cartclass)
ax.set_xlabel('Varvnummer')
ax.set_ylabel('Tid [s]')
ax2.set_xlabel('Varvnummer')
ax2.set_ylabel('Tid efter ledaren [s]')
plt.savefig("test.png")
#plt.show()
