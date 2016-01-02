from django.http import HttpResponse
from django.shortcuts import render
import db

#TODO Make node visualization html pages and make connections
#TODO Edit worldfromscratch

def home(request):
	return HttpResponse("Welcome to the Intellectual Sharing API!")

# POST data must contain 'typeName', 'name', and 'description'
def addNode(request):
	typeName = request.POST.get('typeName')
	if not isinstance(typeName, basestring):
		return HttpResponse("Typename must be a string")
	if typeName == 'TypeNode':
		return HttpResponse("You may not create a central node form this API")

	typeNode = db.getCentralType(db.centralPrefix + request.POST.get('typeName'))
	if typeNode != None:
		name = request.POST.get('name')
		description = request.POST.get('description')
		if isinstance(description, basestring) and isinstance(name, basestring):
			db.createNode(typeName, name, description)
			return HttpResponse("Node created")
		else:
			return HttpResponse("name and description must be strings")
	else:
		return HttpResponse("Type node not found " + typeNode + ".  Would you like to add it to the meta?")
			
def addPropertyToNode(request):
	nodeType = request.POST.get('type')
	name = request.POST.get('name')
	propName = request.POST.get('propName')
	propValue = request.POST.get('propValue')
	if areElementsString(nodeType, name, propName):
		node = db.getNode(nodeType, name)
		if node == None:
			return HttpResponse('No node found')
		else:
			node[propName] = propValue
			node.push()
			return HttpResponse('Property Added Sucessfully')
	else:
		return HttpResponse("type, name, and propName must be strings")

# POST data must contain 'nodeToType', 'nodeToName',
# 'nodeFromType', 'nodeFromName', relationshipName
def addRelationshipToNodes(request):
	if not areElementsString(request.POST.get('nodeToType'), 
		request.POST.get('nodeToName'), request.POST.get('nodeFromType'), 
		request.POST.get('nodeFromName')):
		return HttpResponse('nodeToType, nodeToName, nodeFromType, nodeFromName must be strings')
	nodeTo = db.getNode(request.POST.get('nodeToType'), request.POST.get('nodeToName'))
	nodeFrom = db.getNode(request.POST.get('nodeFromType'), request.POST.get('nodeFromName'))
	if nodeTo != None and nodeFrom != None:
		relationshipName = request.POST.get('relationshipName')
		if isinstance(relationshipName, basestring):
			if db.isRelationshipOnTypeNode(relationshipName, request.POST.get('nodeFromType'), request.POST.get('nodeToType')):
				db.createRelationship(nodeFrom, relationshipName, nodeTo)
				return HttpResponse("Relationship created successfully")
			else:
				# TODO make render page
				# What do we do if the relationship wasn't on the type node?
				return HttpResponse("Relationship wasn't on central typeNode, would you like to add it to the meta?")

		else:
			return HttpResponse("relationshipName must be a string")
	
	else:
		return HttpResponse("Nodes couldn't be found" + str(nodeTo) + str(nodeFrom))

def addMetaNode(request):
    if request.method == 'POST':
        return HttpResponse("post!")
    else:
        rels = db.getRelationshipNames()
        types = db.getTypeNames()
        return render(request, 'addMetaNode.html', {"rels":rels, "types":types})

def viewNode(request, label, name):
    node = db.getNode(label, name)
    if node != None:
        return render(request, 'node.html', {"node": node})
    else:
        return HttpResponse('Node not found.')



def areElementsString(*args):
	for i in args:
		if not isinstance(i, basestring):
			return False
	return True

