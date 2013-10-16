from rdflib import Graph
from sets import Set

class AlignmentProcess():
    
    onto1 = None
    onto2 = None

    def _bind_prefixes(self, ontology):
        ontology.bind('owl', 'http://www.w3.org/2002/07/owl#')

    def _get_properties(self, ontology):
        prop_list = Set()
        sparql_result = ontology.query('SELECT DISTINCT ?s WHERE { ?s a owl:ObjectProperty}')
        for s in sparql_result:
            prop_list.add(s)
        
        sparql_result = ontology.query('SELECT DISTINCT ?s WHERE { ?s a owl:DatatypeProperty}')
        for s in sparql_result:
            prop_list.add(s)
        return prop_list
        
    def _get_classes(self, ontology):
        class_list = Set()
        sparql_result = ontology.query('SELECT DISTINCT ?s WHERE {?s a owl:Class}')
        for s in sparql_result:
            class_list.add(s)
        return class_list
        
    def _get_entity_name(self, prop):
        if '#' in prop.s:
            root = prop.s.defrag()
            return prop.s.split(root)[1][1:]
        else:
            splitted_uri = prop.s.split('/')
            return splitted_uri[len(splitted_uri) - 1]

    def init(self, uri1, uri2):
        self.onto1 = Graph()
        
        self.onto1.parse(uri1, format='xml')
        self._bind_prefixes(self.onto1)
        
        self.onto2 = Graph()
        self.onto2.parse(uri2, format='xml')
        self._bind_prefixes(self.onto2)
        
    def align(self):
        if self.onto1 != None and self.onto2 != None:            
            # Create property lists and matrix
            prop_list1 = self._get_properties(self.onto1)
            prop_list2 = self._get_properties(self.onto2)
            prop_matrix = [[0 for x in xrange(len(prop_list1) + 1)] for x in xrange(len(prop_list2) + 1)]
             
            # Create class lists and matrix
            class_list1 = self._get_classes(self.onto1)
            class_list2 = self._get_classes(self.onto2)
            class_matrix = [[0 for x in xrange(len(class_list1) + 1)] for x in xrange(len(class_list2) + 1)]

            for prop in prop_list1:
                entity_name = self._get_entity_name(prop)
                print entity_name
