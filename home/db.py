from py2neo import *

g = Graph('http://neo4j:django@127.0.0.1:7474/db/data/')


# Wrapping py2neo to give a domain-specific interface for our application

# NOTE: Most methods take instances of Node as arguments, except for the ones that create new Nodes/Relationships

# Helpful method to parse a cypher result
def findSingleNodeFromCypherResult(result):
    order = result.to_subgraph().order
    if order == 0:
        return None
    elif order == 1:
        return result[0][0]
    else:
        print "Error multiple nodes found when single node expected in " + str(result)
        return None

# --- META METHODS ---

def getTypeNode(typeName):
    typeName = typeName.title()
    result = g.cypher.execute("MATCH (n:TypeNode {name:'" + typeName + "'}) RETURN n")
    return findSingleNodeFromCypherResult(result)

def getRelationshipType(relName):
    relName = relName.title()
    result = g.cypher.execute("MATCH (n:RelationshipType {name: '" + relName + "'}) RETURN n")
    return findSingleNodeFromCypherResult(result)
   
def getRelationshipTypeNameBetweenTypeNodes(fromType, toType):
    for rel in fromType.match("HAS_RELATIONSHIP"):
        if rel['forwardRelated'] == toType['name']:
            return rel.end_node['name']
    return None

def getRelationshipTypeNames():
    result = g.cypher.execute("MATCH (n:RelationshipType) RETURN n")
    relNames = []
    for rel in result:
        relNames.append(rel.n["name"])
    return relNames

def getTypeNames():
    result = g.cypher.execute("MATCH (n:TypeNode) RETURN n")
    typeNames = []
    for n in result:
        typeNames.append(n.n['name'])
    return typeNames

def createTypeNode(name):
    name = name.title()
    n = Node("TypeNode", name=name)
    g.create(n)
    return n

def createRelationshipType(relationshipName):
    relationshipName = relationshipName.title()
    relType = Node("RelationshipType", name=relationshipName)
    g.create(relType)
    return relType

def connectTypeNodes(typeFrom, relType, typeTo):
    if relType['name'] == getRelationshipTypeNameBetweenTypeNodes(typeFrom, typeTo):
        return "Connection exists"
    fromToRel = Relationship(typeFrom, "HAS_RELATIONSHIP", relType)
    fromToRel['forwardRelated'] = typeTo['name']
    relToTo = Relationship(relType, "HAS_RELATIONSHIP", typeTo)
    relToTo['backwardRelated'] = typeFrom['name']
    g.create(fromToRel, relToTo)
    return "Type Nodes connected!"


# ----- NON META METHODS ------ 

def createNode(typeName, name):
    typeName = typeName.title()
    node = Node(typeName, name=name)
    g.create(node)
    return node

def createRelationship(nodeFrom, relationship, nodeTo):
    rel = Relationship(nodeFrom, relationship, nodeTo)
    g.create(rel)
    return rel

def getNode(typeName, name):
    typeName = typeName.title()
    result = g.cypher.execute("MATCH (n:" + typeName + " {name:'" + name + "'}) RETURN n")
    return findSingleNodeFromCypherResult(result)

def getOutgoingRels(node):
    if 'TypeNode' in node.labels:
        print "This method does not work for TypeNodes"
        return None
    else:
        rels = []
        for i in node.match_outgoing():
            rels.append((i.type, i.end_node.labels.pop(), i.end_node['name']))
        return rels

def getIncomingRels(node):
    if 'TypeNode' in node.labels:
        print "This method does not work for TypeNodes"
        return None
    else:
        rels = []
        for i in node.match_incoming():
            rels.append((i.type, i.start_node.labels.pop(), i.start_node['name']))
        return rels
