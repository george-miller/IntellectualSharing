from django.views.generic import View
from django.http import HttpResponse, JsonResponse
import json
from .. import db

class ApiRequest(View):
	def __init__(self, postKeys, requiredProps, namesToCheck):
		self.postKeys = postKeys
		self.namesToCheck = namesToCheck
		self.requiredProps = requiredProps

	def get(self, request):
		return HttpResponse("Only POST requests supported", status=400)

	def post(self, request):
		result = self.parsePostRequest(request)
		if result != None:
			return result

		itemsToCheck = []
		for name in self.namesToCheck:
			itemsToCheck.append(self.requiredKeys[name])
		result = self.checkNames(itemsToCheck)
		if result != None:
			return result

		return None

	def getNodes(self, *nodes):
		nodesToReturn = []
		for node in nodes:
			nodeResult = None
			if node[0] == 'TypeNode':
				nodeResult = db.getTypeNode(node[1])
			elif node[0] == 'RelationshipType':
				nodeResult = db.getRelationshipType(node[1])
			else:
				nodeResult = db.getNode(node[0], node[1])
			nodesToReturn.append(nodeResult)
		return nodesToReturn

	# Generate differentiators and requiredKeys from a post request
	def parsePostRequest(self, request):
		requestJson = json.loads(request.body)

		self.properties = {}
		if 'properties' in requestJson.keys():
			self.properties = requestJson['properties']
		for prop in self.requiredProps:
			if prop not in self.properties:
				return HttpResponse("You must specify these properties: " + str(self.requiredProps), status=400)

		self.requiredKeys = {}
		requiredKeysFound = 0
		for key in requestJson.keys():
			key = str(key)
			if key in self.postKeys:
				self.requiredKeys[key] = requestJson[key]
				requiredKeysFound+=1
		if len(self.postKeys) > requiredKeysFound:
			return HttpResponse("You must specify these keys: " + str(self.postKeys), status=400)
		return None

	def checkNames(self, names):
		for name in names:
			if not self.isValidTypeOrRelTypeName(name):
				return HttpResponse(self.typeRuleMessage(name), status=400)
		return None

	def isValidTypeOrRelTypeName(self, typeName):
		letters = list(typeName)
		for letter in letters:
			if not letter.isalnum() and not letter == '_':
				return False
		return True

	def typeRuleMessage(self, typeName):
		return "Invalid Type Name: "+typeName+".  Types must only contain letters, numbers, and underscores"

	def nodeString(self, typeName, properties):
	    return "Node - " + typeName + " : " + str(properties)

	def relString(self, relName, fromType, fromName, toType, toName):
	    return "Relationship - " + relName + " from " + nodeString(fromType, fromName) + " to " + nodeString(toType, toName)
