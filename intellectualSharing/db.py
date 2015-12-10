from py2neo import *

authenticate('localhost:7474', 'neo4j', 'django')
g = Graph()

# Wrapping py2neo to give a domain-specific interface for our application

def getCentralType(typeName):
	t = g.find_one("__" + typeName)
	return t
	
def createNode(typeName, name, description):
	node = Node(typeName, name=name, description=description)
	g.create(node)


def createRelationship(nodeFrom, relationship, nodeTo):
	rel = Relationship(nodeFrom, relationship, nodeTo)
	g.create(rel)

def getNode(label, name):
	if isinstance(label, basestring) and isinstance(name, basestring):
		result = g.cypher.execute("MATCH (n:" + label + " {name:'" + name + "'}) RETURN n")
		order = result.to_subgraph().order
		if order == 0:
			return None
		elif order == 1:
			return result[0][0]
		else:
			return "Error multiple nodes found with name " + name + " and label " + label
	else:
		return "label and name must be strings"

def isRelationshipOnTypeNode(relationship, nodeFromType, nodeToType):
	fromType = getCentralType(nodeFromType)
	toType = getCentralType(nodeToType)
	if (fromType != None and toType != None):
		rels = fromType.match(relationship)
		r = None
		for rel in rels:
			if r == None:
				r = rel
			else:
				return "Error multiple relationships on typeNode with same name"
		# Search in the endNode of r for a label that matches toType
		for label in r.nodes[1].labels:
			if label == ("__" + nodeToType):
				return True

		# NodeToType didn't match the one on the central type node
		return False

	else:
		return False
		