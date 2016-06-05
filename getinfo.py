#!/usr/bin/python

from subprocess import check_output
from rpmUtils.miscutils import compareEVR
from rpmUtils.miscutils import splitFilename

import xml.etree.cElementTree as etree
import platform


os_arch = platform.machine()
os_release = platform.dist()[1][0]
tree = etree.parse('errata.latest.xml')
root = tree.getroot()


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

rpmPkgs = {}
rpmStream = check_output(['rpm', '-qa', "--queryformat=%{name}-%{version}-%{release}.%{arch}.rpm\n"]).splitlines()



for pkgLine in rpmStream:
	pkg = splitFilename(pkgLine)
	rpmPkgs[pkg[0]] = {'version': pkg[1], 'release': pkg[2], 'epoch': pkg[3], 'arch': pkg[4]}

#print rpmPkgs



for node in root:
	if node.tag == 'meta': continue
#	if not IsAppliable( node, 'os_release', os_release ): continue
	if not IsAppliable( node, 'os_arch', os_arch ):		  continue
	for pkgLine in node.iter( 'packages' ):
		pkg = splitFilename( pkgLine.text )
		if pkg[0] in rpmPkgs:
			insPkg = rpmPkgs[ pkg[0] ]
			insPkg = [ insPkg['epoch'], insPkg['version'], insPkg['release'] ]
			errPkg = [ pkg[3], pkg[1], pkg[2]  ]
			if compareEVR( errPkg, insPkg ) > 0:
				print node.tag + " " + pkg[0]
				print "Installed: " 
				print insPkg
				print "Errata: " 
				print errPkg
				print ''

