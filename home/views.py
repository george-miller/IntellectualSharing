from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import db
import json

def nodeString(typeName, properties):
    return "Node - " + typeName + " : " + properties

def relString(relName, fromType, fromName, toType, toName):
    return "Relationship - " + relName + " from " + nodeString(fromType, fromName) + " to " + nodeString(toType, toName)

def home(request):
    print request.body
    return render(request, 'is.html')

# ------ NON-META API ------

def viewNode(request):
    typeName = request.GET.get('typeName')
    name = request.GET.get('name')

    checkNameResult = viewsHelper.checkNames(typeName)
    if checkNameResult != True:
        return checkNameResult

    [nodetemp] = viewsHelper.getNodes(request, [typeName, name])
    node = db.TemplateNode(nodetemp)
    if node != None:
        return render(request, 'node.html',
            {
            'node': node,
            "outgoingRels": db.getOutgoingRels(nodetemp),
            "incomingRels": db.getIncomingRels(nodetemp)
            })
    else:
        return HttpResponse(nodeString(typeName, name)+' not found.', status=404)

def viewNodeType(request):
    typeName = request.GET.get('typeName')
    checkNameResult = viewsHelper.checkNames(typeName)
    if checkNameResult != True:
        return checkNameResult

    nodes = db.getNodesByType(typeName)
    if nodes != []:
        return render(request, 'nodes.html',{'nodes': nodes, 'nodeType': typeName})
    else:
        return HttpResponse(nodeString(typeName, name)+' not found.', status=404)



# ----- META API ------

def typeNodeEditor(request):
    rels = db.getRelationshipTypeNames()
    types = db.getTypeNames()
    return render(request, 'typeNodeEditor.html', {"rels":rels, "types":types})
