from rdflib import Graph
from stringdistances import substring_distance

class AlignmentProcess():
    
    onto1 = None
    onto2 = None

    def _bind_prefixes(self, ontology):
        ontology.bind('owl', 'http://www.w3.org/2002/07/owl#')

    def _get_properties(self, ontology):
        prop_list = []
        sparql_result = ontology.query('SELECT DISTINCT ?s WHERE { ?s a owl:ObjectProperty}')
        for s in sparql_result:
            if s not in prop_list:
                prop_list.append(s)
        
        sparql_result = ontology.query('SELECT DISTINCT ?s WHERE { ?s a owl:DatatypeProperty}')
        for s in sparql_result:
            if s not in prop_list:
                prop_list.append(s)
        return prop_list
        
    def _get_classes(self, ontology):
        class_list = []
        sparql_result = ontology.query('SELECT DISTINCT ?s WHERE {?s a owl:Class}')
        for s in sparql_result:
            if s not in class_list:
                class_list.append(s)
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
        #Parameters
        pia = 1.0 # relation weight for name
        pic = 0.5 # class weigth for name
        epsillon = 0.05 # stoping condition 
        threshold = 1.0 # threshold above which distances are too high
 
        if self.onto1 != None and self.onto2 != None:            
            # Create property lists and matrix
            prop_list1 = self._get_properties(self.onto1)
            prop_list2 = self._get_properties(self.onto2)
            prop_matrix = [[0 for x in xrange(len(prop_list2))] for x in xrange(len(prop_list1))]
             
            # Create class lists and matrix
            class_list1 = self._get_classes(self.onto1)
            class_list2 = self._get_classes(self.onto2)
            class_matrix = [[0 for x in xrange(len(class_list2))] for x in xrange(len(class_list1))]

            i = 0
            for prop1 in prop_list1:
                j = 0;
                entity_name1 = self._get_entity_name(prop1)
                if entity_name1 != None:
                    entity_name1 = entity_name1.lower()
                
                for prop2 in prop_list2:
                    entity_name2 = self._get_entity_name(prop2)
                    if entity_name2 != None:
                        entity_name2 = entity_name2.lower()
                    
                    if entity_name1 != None or entity_name2 != None:                
                        prop_matrix[i][j] = pia * substring_distance(entity_name1, entity_name2)
                    else:
                        prop_matrix[i][j] = 1.0
                    j += 1
                i += 1
                
            i = 0            
            for class1 in class_list1:
                j = 0
                entity_name1 = self._get_entity_name(class1)
                if entity_name1 != None:
                    entity_name1 = entity_name1.lower()
                    
                for class2 in class_list2:
                    entity_name2 = self._get_entity_name(class2)
                    if entity_name2 != None:
                        entity_name2 = entity_name2.lower()
                    class_matrix[i][j] = pic * substring_distance(entity_name1, entity_name2)
                    j += 1
                i += 1
                
            factor = 1.0
            while factor > epsillon:
                for i in xrange(len(prop_list1)):
                    found = False
                    best = 0
                    max_value = threshold
                    for j in xrange(len(prop_list2)):
                        if prop_matrix[i][j] < max_value:
                            found = True
                            best = j
                            max_value = prop_matrix[i][j]
                    if found and max_value < 0.5:
                        print prop_list1[i], prop_list2[best], 1.0 - max_value
