#! /usr/bin/env python

import datetime
import os
import subprocess
import sys
import commands

#Input the NFS path or local file with forward slash (/) at the end.
#example: NFSPATH = "/var/run/sr-mount/111111ee-99ww-iw9w-jcw8-7394792jd83e/"
NFSPATH = " "

# Object that holds the name and uuid of a virtual machine
class VirtualMachine(object):
	name = " "

	uuid = " "

	
	def insertName(self,name):
		self.name = name


	def insertUUID(self,uuid):
		self.uuid = uuid
	

#stores all virtual machine name & uuid information into the vmList variable.
vmList = commands.getoutput("xe vm-list is-control-domain=false is-a-snapshot=false | grep 'uuid\|name-label' | cut -d ':' -f2")

#initialize the list which will have VM objects stored into it.
listofVM=[]

counter = 0

indexNum = 0


#this for loop is responsible for assigning name values to the name variable in the VirtualMachine objects.
#VirtualMachine objects are created within this loop and appended into listofVM[]
for line in vmList.splitlines():

	counter+=1
	line = line.strip()
	VMObject = VirtualMachine()	
	#use counter mod 2 = 0 so that it only reads every other line.
	if counter % 2 == 0:
		VMObject.insertName(line)
		listofVM.append(VMObject)	

		indexNum += 1

#this for loop is responsible for assigning UUID values to the UUID variable in the VirtualMachine objects.
counter = 0;
indexNum=0
for line in vmList.splitlines():
	counter +=1
	line = line.strip()
	if counter %2 != 0:

		listofVM[indexNum].insertUUID(line)
		
		indexNum +=1		

#_____________________code above only creates the virtual machine information objects_________________________

#This loop reads the list of virtual machine objects and performs backups individually. 
for VirtualMachine in listofVM:

	todaysdate = datetime.date.today()
	snapshotUUID = " "
	systemvar = 0
	
	print("Starting backup process for " + VirtualMachine.name)
	print("Creating snapshot for " + VirtualMachine.name)
	snapshotUUID = commands.getoutput("xe vm-snapshot uuid='%s' new-name-label='%s_%s'" %(VirtualMachine.uuid, VirtualMachine.name,todaysdate))
	
	print("Converting snapshot to VM")
	#template set
	systemvar = os.system("xe template-param-set is-a-template=false ha-always-run=false uuid='%s'" %snapshotUUID)
	if systemvar == 0:
		print("conversion successful")
	else: 
		print("Something went wrong: \n")
		print(systemvar)
		sys.exit()
	
	print("Exporting " + VirtualMachine.name + " backup to file path")
	#export backup into NFS
	systemvar = os.system("xe vm-export vm='%s' filename='%s%s_backup%s.xva'" %(snapshotUUID,NFSPATH,VirtualMachine.name,todaysdate))
	if systemvar == 0:
		print("Backup successful")
	else: 
		print("Something went wrong: \n")
		print(systemvar)
		
	#delete snapshot
	os.system("xe vm-uninstall uuid='%s' force=true" %snapshotUUID)
