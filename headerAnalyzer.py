#!/usr/bin/python
#coding=utf-8

# # # # # # # 
# objectiv-c headers analyzer 0.0.1
# # # # # # # 
# @interface  @protocol @property
# public methods

import os
import time
import sys
import re

r_class = re.compile('^(\s*@interface\s*)(\w+)(\s*:\s*\w+|\s*\(\w*\)\s*)') # @interface AMapService : NSObject
r_protocol = re.compile('^(\s*@protocol\s*)(\w+)(\s*<\w*>\s*)') # @protocol AMapComponent <NSObject>
r_property = re.compile('^(\s*@property.+;+)') # @property (nonatomic, readonly) NSString *name;

# - (void)sendInitInfoWithComponent:(id<AMapComponent>)component;
# + (NSDictionary *)commonHTTPHeadersWithComponent:(id<AMapComponent>)component;
r_methodSingleLine = re.compile('^(\s*\+?\-?\s*\(.+\).+;+.*)') 
r_methodStart = re.compile('^(\s*\+?\-?\s*\(.+\).+)') 
r_methodEnd = re.compile('^([^+-]*;+.*)') 

r_end = re.compile('\s*@end') 

g_clazzList = []
g_protocolList = []
g_propertyMapping = {} #{'className': propertList}
g_methodMapping = {} #{'className': methodList}
g_protoMethodMapping = {} #{'protoName': methodList} 属于proto的属性和方法。

g_fileCount = 0

# type 1 class, 2 protocol, typeName 是类名或协议名
def addProperty(propertyName, listType, typeName): 
	propertyList = []

	if listType == 1:
		if not g_propertyMapping.has_key(typeName):
			g_propertyMapping[typeName] = propertyList
		else :
			propertyList = g_propertyMapping[typeName]
	elif listType == 2:
		if not g_protoMethodMapping.has_key(typeName):
			g_protoMethodMapping[typeName] = propertyList
		else :
			propertyList = g_protoMethodMapping[typeName]

	propertyList.append(propertyName)	

# type 1 class, 2 protocol
def addMethod(methodName, listType, typeName):
	methodList = []

	if listType == 1:
		if not g_methodMapping.has_key(typeName):
			g_methodMapping[typeName] = methodList
		else :
			methodList = g_methodMapping[typeName]
	elif listType == 2:
		if not g_protoMethodMapping.has_key(typeName):
			g_protoMethodMapping[typeName] = methodList
		else :
			methodList = g_protoMethodMapping[typeName]

	methodList.append(methodName)	

# 返回(name, type), type: -1 valid, 0 end, 1 class, 2 protocol, 3 property, 4 method, 5 method end.
def processLine(oneLine):
	lineType = -1
	lineInfo = oneLine
	m = r_end.match(oneLine)
	while True:
		if m: #is end
			lineType = 0
			break

		m = r_class.match(oneLine)
		if m: #is class
			lineInfo = m.expand(r'\2')
			lineType = 1
			break

		m = r_protocol.match(oneLine)
		if m: #is protocol
			lineInfo = m.expand(r'\2')
			lineType = 2
			break

		m = r_property.match(oneLine)
		if m: #is property
			lineInfo = m.expand(r'\1')
			lineType = 3
			break
		m = r_methodStart.match(oneLine)
		if m: #is method start

			lineInfo = m.expand(r'\1')
			lineType = 4
			m = r_methodSingleLine.match(oneLine)
			if m: #is method end
				lineType = 5
			
			break
		m = r_methodEnd.match(oneLine)
		if m: #is method end
			lineInfo = m.expand(r'\1')
			lineType = 5
			break
		# finally break	
		break

	return (lineInfo, lineType)

def processHeader(headerFile):

	currentClass = ""
	currentProto = ""
	currentMethod = ""

	f = open(headerFile)             # 返回一个文件对象  
	line = f.readline()	 # 调用文件的 readline()方法  
	while line:
		if(line == ""):
			break
		# print "ooooo" + line.strip('\n')
		currentLine = processLine(line.strip('\n'))
		# print currentLine

		lineType = currentLine[1]
		lineString = currentLine[0]

		if lineType < 0:
			if currentMethod != "": # 分行方法进行中
				currentMethod = currentMethod + "\n" + lineString
		elif lineType == 0: #end
			currentClass = ""
			currentProto = ""
		elif lineType == 1: #class
			currentClass = lineString
			if currentClass not in g_clazzList:
				g_clazzList.append(currentClass)
		elif lineType == 2: #protocol
			currentProto = lineString
			if lineString not in g_protocolList:
				g_protocolList.append(lineString)
		elif lineType == 3: #property
			if currentClass != "":
				addProperty(lineString, 1, currentClass)
			elif currentProto != "":
				addProperty(lineString, 2, currentProto)
		elif lineType == 4: #method start
			currentMethod = lineString
			# if currentClass != "":
			# 	addMethod(lineString, 1, currentClass)
			# elif currentProto != "":
			# 	addMethod(lineString, 2, currentProto)	
		elif lineType == 5: #method end
			if currentMethod == "":
				currentMethod = lineString	
			else :
				currentMethod = currentMethod + "\n" + lineString

			if currentClass != "":
				addMethod(currentMethod, 1, currentClass)
			elif currentProto != "":
				addMethod(currentMethod, 2, currentProto)
			currentMethod = ""

		line = f.readline()
	f.close()

def getFileList(dir, fileList):
	newDir = dir
	if os.path.isfile(dir):
		# 匹配头文件
		r_header = re.compile('^\w+.h') 
		fileName = os.path.split(dir)[1]
		if r_header.match(fileName):
			fileList.append(dir.decode('utf-8'))
	elif os.path.isdir(dir):
		files = os.listdir(dir)
		for s in files:
			newDir = os.path.join(dir,s)
			getFileList(newDir, fileList)  

	return fileList

def saveResult():

	timeString = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
	fileName = "analytics_result-" + "timeString" + ".txt"
	result = open(fileName, 'w')

	totalPropertyCount = 0
	totalMethodCount = 0
	totalProtoMethodCount = 0

	# class
	classInfo = "Class : %d" % len(g_clazzList)
	result.write(classInfo + '\n')
	result.write("*********************\n")
	# print g_propertyMapping
	# print g_methodMapping
	for value in g_clazzList:
		# print value
		propertyList = g_propertyMapping.get(value)
		methodList = g_methodMapping.get(value)

		propertyCount = 0
		methodCount = 0

		if propertyList:
			propertyCount = len(propertyList)
		if methodList:
			methodCount = len(methodList)
		
		totalPropertyCount += propertyCount
		totalMethodCount += methodCount

		infoString = "%s (p :%d, m :%d) \n" % (value, propertyCount, methodCount)
		result.write(infoString)

		if propertyCount > 0:
			for oneItem in propertyList:
				result.write(oneItem + "\n")
			result.write("\n")

		if methodCount > 0:
			for oneItem in methodList:
				result.write(oneItem + "\n")
		
		result.write("\n")

	# protocol issues
	protoInfo = "Protocol : %d" % len(g_protocolList)
	result.write(protoInfo + '\n')
	result.write("*********************\n")

	for value in g_protocolList:
		methodList = g_protoMethodMapping.get(value)
		methodCount = 0

		if methodList:
			methodCount = len(methodList)
		
		totalProtoMethodCount += methodCount

		infoString = "%s (m :%d) \n" % (value, methodCount)
		result.write(infoString)

		if methodCount > 0:
			for oneItem in methodList:
				result.write(oneItem + "\n")
			result.write("\n")
	
	# end
	fileInfo = "File :%d" % g_fileCount
	propertyInfo = "Property : %d" % totalPropertyCount
	methodInfo =  "Method   : %d" % totalMethodCount
	protoMethodInfo =  "Proto Method : %d" % totalProtoMethodCount

	result.write("*********************\n")
	result.write(fileInfo + '\n')
	result.write(classInfo + '\n')
	result.write(protoInfo + '\n')
	result.write(propertyInfo + '\n')
	result.write(methodInfo + '\n')
	result.write(protoMethodInfo + '\n')
	result.write("\n")
	result.write("Created at %s \n" % timeString)
	result.write("\n")
	result.close()

	# print result info
	print fileInfo
	print classInfo
	print protoInfo
	print propertyInfo
	print methodInfo
	print protoMethodInfo

	print "The result was saved to file [%s]" % fileName


def showHelp():
    print "Please using this script like this \"python headerAnalyzer.py [HeaderDirectory]\" or \"./headerAnalyzer.py [HeaderDirectory]\"."
    print "The default [HeaderDirectory] is \"Headers\"."
    

if __name__ == '__main__':
    args = sys.argv
    showHelp()

    if len(args) >= 2:
    	dirName = args[1]
    else :
    	dirName = "Headers"

    homeDir = os.getcwd()
    # 指定文件夹
    headerDir = os.path.join(homeDir, dirName)
    # print headerDir
    fileList = getFileList(headerDir, [])

    for e in fileList:
    	g_fileCount += 1
    	processHeader(e)

    saveResult()





