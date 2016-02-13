from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import db
import viewsHelper

#TODO check if node/relationship is in DB before adding it.
#TODO TESTS
#TODO Strict input checking
#TODO allow reverse direction relationships

#TODO Save name with input cases, then when trying to access a node, match to any node with with the same letters regardless of case
#TODO Edit worldfromscratch

def nodeString(typeName, name):
    return "Node - " + typeName + " : " + name

def relString(relName, fromType, fromName, toType, toName):
    return "Relationship - " + relName + " from " + nodeString(fromType, fromName) + " to " + nodeString(toType, toName)

def home(request):
    return render(request, 'index.html')

# ------ NON-META API ------

#TODO add properties to request
# POST data must contain 'typeName' and 'name'
def addNode(request):
    parseResult = viewsHelper.parsePostRequest(request, 'typeName', 'name')
    if parseResult[0] == False:
        return parseResult[1]
    (typeName, name) = parseResult

    checkNameResult = viewsHelper.checkNames(typeName)
    if checkNameResult != True:
        return checkNameResult

    if typeName == 'TypeNode':
        return HttpResponse("You may not create a meta node with this API call, try /createTypeNode", status=400)

    #TODO properties could differentiate
    # find single match of property, that is a match
    [typeNode, node] = viewsHelper.getNodes(request, ['TypeNode', typeName], [typeName, name])

    if typeNode == None:
        return HttpResponse("Type node not found with typeName " + typeName, status=404)
    elif type(typeNode).__name__ == 'HttpResponse':
        return typeNode
    else:
        if node == None:
            db.createNode(typeName, name)
            return HttpResponse(nodeString(typeName, name)+" created", status=201)
        elif type(node).__name__ == 'HttpResponse':
            return node
        else:
            return HttpResponse(nodeString(typeName, name)+" exists", status=200)

#TODO Mutliple Property Request
# required POST data: 'typeName', 'name', 'propName', 'propValue'           
def addPropertyToNode(request):
    parseResult = viewsHelper.parsePostRequest(request, 'typeName', 'name', 'propName', 'propValue')
    if parseResult[0] == False:
        return parseResult[1]
    [typeName, name, propName, propValue] = parseResult

    checkNameResult = viewsHelper.checkNames(typeName)
    if checkNameResult != True:
        return checkNameResult

    [node] = viewsHelper.getNodes(request, [typeName, name])
    if node != None:
        node[propName] = propValue
        node.push()
        return HttpResponse('Property '+propName+' : '+propValue+
            ' Added to '+nodeString(typeName, name)+' Sucessfully', status=201)
    else:
        return HttpResponse(nodeString(typeName, name)+" was not found", status=404)

# POST data must contain 'toType', 'toName', 'fromType', 'fromName', 'relName'
def addRelationshipBetweenNodes(request):
    parseResult = viewsHelper.parsePostRequest(request, 'toType', 'toName', 'fromType', 'fromName', 'relName')
    if parseResult[0] == False:
        return parseResult[1]
    [toType, toName, fromType, fromName, relName] = parseResult

    relName = viewsHelper.fixTypeOrRelTypeNameCases(relName)

    checkNameResult = viewsHelper.checkNames(toType, fromType, relName)
    if checkNameResult != True:
        return checkNameResult

    [nodeFrom, nodeTo,  fromTypeNode, toTypeNode] = viewsHelper.getNodes(request, 
        [fromType, fromName], [toType, toName], ['TypeNode', fromType], ['TypeNode', toType])
    if nodeTo != None and nodeFrom != None:
        if fromTypeNode != None and toTypeNode != None:
            # Is a realtionship with this name in the meta?
            possibleRels = db.getRelationshipTypeNamesBetweenTypeNodes(
                fromTypeNode,
                toTypeNode
                )
            if relName in possibleRels:
                if db.isRelationshipBetweenNodes(nodeFrom, relName, nodeTo):
                    return HttpResponse(relString(relName, fromType, fromName, toType, toName)+
                        " already exists", status=200)
                else:
                    db.createRelationship(nodeFrom, relName, nodeTo)
                    return HttpResponse(relString(relName, fromType, fromName, toType, toName)+
                        " created successfully!", status=201)
            else:
                # TODO make render page
                # What do we do if the relationship wasn't in the meta?
                return HttpResponse(relString(relName, fromType, fromName, toType, toName)+
                    " wasn't in the meta. Possible relationships: "+str(possibleRels), status=404)
        else:
            return HttpResponse("TypeNodes couldn't be found for types: "+fromType+" and "+toTypeNode, status=404)
    else:
        return HttpResponse("Nodes couldn't be found: NodeFrom: "+
            nodeString(fromType, fromName)+" NodeTo: "+
            nodeString(toType, toName), status=404)

def viewNode(request, typeName, name):
    checkNameResult = viewsHelper.checkNames(typeName)
    if checkNameResult != True:
        return checkNameResult

    [node] = viewsHelper.getNodes(request, [typeName, name])
    if node != None:
        return render(request, 'node.html', 
            {"nodeType": node.labels.pop(),
            "nodeName": node['name'], 
            "outgoingRels": db.getOutgoingRels(node), 
            "incomingRels": db.getIncomingRels(node)
            })
    else:
        return HttpResponse(nodeString(typeName, name)+' not found.', status=404)


# ----- META API ------

# Required POST data: 'typeName'
def createTypeNode(request):
    parseResult = viewsHelper.parsePostRequest(request, 'typeName')
    if parseResult[0] == False:
        return parseResult[1]
    [typeName] = parseResult

    checkNameResult = viewsHelper.checkNames(typeName)
    if checkNameResult != True:
        return checkNameResult

    [typeNode] = viewsHelper.getNodes(request, ['TypeNode', typeName])
    if typeNode == None:
        db.createTypeNode(typeName)
        return HttpResponse("Type Node "+typeName+" created", status=201)
    else:
        return HttpResponse("Type Node "+typeName+" exists", status=200)

# Required POST data: 'relName'
def createRelationshipType(request):
    parseResult = viewsHelper.parsePostRequest(request, 'relName')
    if parseResult[0] == False:
        return parseResult[1]
    [relName] = parseResult

    checkNameResult = viewsHelper.checkNames(relName)
    if checkNameResult != True:
        return checkNameResult

    [relType] = viewsHelper.getNodes(request, ['RelationshipType', relName])
    print relName+str(relType)
    if relType == None:
        db.createRelationshipType(relName)
        return HttpResponse("Relationship Type "+relName+" created", status=201)
    else:
        return HttpResponse("Relationship Type "+relName+" exists", status=200)

# Required POST data: 'typeFrom', 'relName', 'typeTo'
def connectTypeNodes(request):
    parseResult = viewsHelper.parsePostRequest(request, 'typeFrom', 'relName', 'typeTo')
    if parseResult[0] == False:
        return parseResult[1]
    [typeFrom, relName, typeTo] = parseResult

    checkNameResult = viewsHelper.checkNames(typeFrom, relName, typeTo)
    if checkNameResult != True:
        return checkNameResult

    [typeFromNode, typeToNode, relType] = viewsHelper.getNodes(request, 
        ['TypeNode', typeFrom], ['TypeNode', typeTo], ['RelationshipType', relName])

    if typeFromNode == None:
        return HttpResponse("Couldn't find typeFrom " + typeFrom, status=400)
    elif typeToNode == None:
        return HttpResponse("Couldn't find typeTo " + typeTo, status=400)
    elif relType == None:
        return HttpResponse("Couldn't find relType from name " + relName, status=400)
    else:
        if relType['name'] in db.getRelationshipTypeNamesBetweenTypeNodes(typeFromNode, typeToNode):
            return HttpResponse("Connection exists: " + typeFrom + " -> " + relName + " -> " + typeTo, status=200)
        else:
            db.connectTypeNodes(typeFromNode, relType, typeToNode)
            return HttpResponse("Connection created " + typeFrom + " -> " + relName + " -> " + typeTo, status=201)

# Required POST data: 'typeName'
def getRelationshipDict(request):
    parseResult = viewsHelper.parsePostRequest(request, 'typeName')
    if parseResult[0] == False:
        return parseResult[1]
    typeName = parseResult[0]

    checkNameResult = viewsHelper.checkNames(typeName)
    if checkNameResult != True:
        return checkNameResult

    [typeNode] = viewsHelper.getNodes(request, ['TypeNode', typeName])
    if typeNode == None:
        return HttpResponse("TypeNode "+typeName+" couldn't be found", status=404)
    else:
        return JsonResponse(db.getRelationshipDict(typeNode), status=200)


def typeNodeEditor(request):
    rels = db.getRelationshipTypeNames()
    types = db.getTypeNames()
    return render(request, 'typeNodeEditor.html', {"rels":rels, "types":types})
