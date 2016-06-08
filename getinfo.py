#!/usr/bin/python

from subprocess import check_output
from rpmUtils.miscutils import compareEVR
from rpmUtils.miscutils import splitFilename
from re import match

import xml.etree.cElementTree as etree
import platform

rpmStreamFile = "1.txt"

os_arch = platform.machine()
os_release = match(r'^\d+', platform.linux_distribution()[1]).group()
tree = etree.parse('errata.latest.xml')
root = tree.getroot()


def GetRpmListFromFile( rpmStreamFile ):
	with open( rpmStreamFile, 'r' ) as rpmStream:
		rpmPkgs = ParseRpmList( rpmStream )
	rpmStream.closed
	return rpmPkgs


def GetRpmListFromRPM():
	rpmStream = check_output(['rpm', '-qa', "--queryformat=%{name}-%{version}-%{release}.%{arch}.rpm\n"]).splitlines()
	return ParseRpmList( rpmStream )


def GetRpmListFromSSH():
	return 0


def ParseRpmList( rpmList ):
	rpmPkgs = {}
	for rpmLine in rpmList:
		rpm = splitFilename( rpmLine )
		rpmPkgs[ rpm[0] ] = { 'version': rpm[1], 
				      'release': rpm[2], 
				      'epoch':   rpm[3], 
				      'arch':    rpm[4]  }
	return rpmPkgs


def GotTagWithValue(node, tag, value):
	for leaf in node.iter(tag):
		if leaf.text == value:
			return True
	return False


def IsAppliable( tree, leaf, marker ):
	leafList = tree.findall(leaf)
	if len(leafList):
		for l in leafList:
			l.text
			if l.text == marker: 
				return True
		return False
	else:
		return True


rpmPkgs =  GetRpmListFromRPM()




reportArray = {}
for node in root:
	if node.tag == 'meta': continue
	if not IsAppliable( node, 'os_release', os_release ): continue
	if not IsAppliable( node, 'os_arch', os_arch ):	      continue
	for pkgLine in node.iter( 'packages' ):
		pkg = splitFilename( pkgLine.text )
		if pkg[0] in rpmPkgs:
			insPkg = rpmPkgs[ pkg[0] ]
			insPkg = [ insPkg['epoch'], insPkg['version'], insPkg['release'] ]
			errPkg = [ pkg[3], pkg[1], pkg[2]  ]
			if compareEVR( errPkg, insPkg ) > 0:
				if not pkg[0] in reportArray:
					reportArray[ pkg[0] ] = []
				reportArray[ pkg[0] ].append({ 
					'err': node.tag, 
					'severity': node.get('severity'), 
					'type': node.get('type'), 
					'description': node.get('description'),
					'version': errPkg[1],
					'release': errPkg[2]
				})
#				print node.tag + " " + pkg[0]
#				print "Installed: " 
#				print insPkg
#				print "Errata: " 
#				print errPkg
#				print ''

for i in reportArray:
	print '\n{} ver. {} rel. {}'.format(i, rpmPkgs[i]['version'], rpmPkgs[i]['release'])
	for a in reportArray[i]:
		print '{}: {} {}. Version: {} {}'.format( a['err'], a['severity'], a['type'], a['version'], a['release'] ) 
