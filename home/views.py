from django.http import HttpResponse
from django.shortcuts import render
import db

#TODO check if node/relationship is in DB before adding it.
#TODO TESTS
#TODO Strict input checking
#TODO allow reverse direction relationships

#TODO Save name with input cases, then when trying to access a node, match to any node with with the same letters regardless of case
#TODO Edit worldfromscratch

def home(request):
    return render(request, 'index.html')

# ------ NON-META API ------

# POST data must contain 'typeName' and 'name'
def addNode(request):
    typeName = request.POST.get('typeName')
    if typeName == 'TypeNode':
        return HttpResponse("You may not create a meta node with this API call")
    typeNode = db.getTypeNode(typeName)
    if typeNode != None:
        name = request.POST.get('name')
        if name == "" or name == None:
            return HttpResponse("name must not be empty")
        else:
            db.createNode(typeName, name)
            return HttpResponse("Node created")
    else:
        return HttpResponse("Type node not found with typeName " + typeName + ".  The type must be in the meta before adding an instance of it")

# required POST data: 'type', 'name', 'propName', 'propValue'           
def addPropertyToNode(request):
    node = db.getNode(request.POST.get('type'), request.POST.get('name'))
    if node != None:
        node[request.POST.get('propName')] = request.POST.get('propValue')
        node.push()
        return HttpResponse('Property Added Sucessfully')
    else:
        return HttpResponse('No node found or other error occurred')


# POST data must contain 'nodeToType', 'nodeToName', 'nodeFromType', 'nodeFromName', 'relationshipName'
def addRelationshipBetweenNodes(request):
    nodeTo = db.getNode(request.POST.get('nodeToType'), request.POST.get('nodeToName'))
    nodeFrom = db.getNode(request.POST.get('nodeFromType'), request.POST.get('nodeFromName'))
    if nodeTo != None and nodeFrom != None:
        relationshipName = request.POST.get('relationshipName')
        if relationshipName == "" or relationshipName == "None":
            return HttpResponse("relationshipName must not be empty")
        else:
            # Is a realtionship with this name in the meta?
            if db.getRelationshipTypeNameBetweenTypeNodes(
                db.getTypeNode(request.POST.get('nodeFromType')),
                db.getTypeNode(request.POST.get('nodeToType'))
                ) == relationshipName:
                db.createRelationship(nodeFrom, relationshipName, nodeTo)
                return HttpResponse("Relationship created successfully")
            else:
                # TODO make render page
                # What do we do if the relationship wasn't in the meta?
                return HttpResponse("Relationship wasn't on TypeNode, would you like to add it to the meta?")
    else:
        return HttpResponse("Nodes couldn't be found, their results were: " + str(nodeTo) + str(nodeFrom))

def viewNode(request, typeName, name):
    node = db.getNode(typeName, name)
    if node != None:
        return render(request, 'node.html', 
            {"nodeType": node.labels.pop(),
            "nodeName": node['name'], 
            "outgoingRels": db.getOutgoingRels(node), 
            "incomingRels": db.getIncomingRels(node)
            })
    else:
        return HttpResponse('Node of type '+typeName+' named '+name+' not found.')


# ----- META API ------

# Required POST data: 'typeName'
def createTypeNode(request):
    if request.method == 'POST':
        typeName = request.POST.get('typeName')
        typeNode = db.getTypeNode(typeName)
        if typeName == "" or typeName == "None":
            return HttpResponse("You must specify a name for your Type Node", status=400)
        elif typeNode == None:
            db.createTypeNode(typeName)
            return HttpResponse("Type Node "+typeName+" created", status=201)
        else:
            return HttpResponse("Type Node "+typeName+" exists", status=200)
    else:
        return HttpResponse("Only POST requests supported", status=400)

# Required POST data: 'relName'
def createRelationshipType(request):
    if request.method == 'POST':
        relName = request.POST.get('relName')
        relType = db.getRelationshipType(relName)
        if relName == "" or relName == "None":
            return HttpResponse("You must specify a name for your Relationship Type", status=400)
        elif relType == None:
            db.createRelationshipType(relName)
            return HttpResponse("Relationship Type "+relName+" created", status=201)
        else:
            return HttpResponse("Relationship Type "+relName+" exists", status=200)
    else:
        return HttpResponse("Only POST requests supported", status=400)

# Required POST data: 'typeFrom', 'relName', 'typeTo'
def connectTypeNodes(request):
    if request.method == 'POST':
        typeFrom = request.POST.get('typeFrom')
        relName = request.POST.get('relName')
        typeTo = request.POST.get('typeTo')
        typeFromNode = db.getTypeNode(typeFrom)
        typeToNode = db.getTypeNode(typeTo)
        relType = db.getRelationshipType(relName)
        if typeFrom == None:
            return HttpResponse("Couldn't find typeFrom " + typeFrom, status=400)
        elif typeTo == None:
            return HttpResponse("Couldn't find typeTo " + typeTo, status=400)
        elif relType == None:
            return HttpResponse("Couldn't find relType from name " + relName, status=400)
        else:
            response = db.connectTypeNodes(typeFromNode, relType, typeToNode)
            return HttpResponse(response + " " + typeFrom + " -> " + relName + " -> " + typeTo, status=201)
    else:
        return HttpResponse("Only POST requests supported", status=400)

def typeNodeEditor(request):
    rels = db.getRelationshipTypeNames()
    types = db.getTypeNames()
    return render(request, 'typeNodeEditor.html', {"rels":rels, "types":types})


