from rdflib import Graph
from rdflib.term import URIRef
import stringdistances
import operator

class AlignmentCell():
        prop1 = None
        prop2 = None
        relation = None
        measure = 0.0
        
        def __init__(self, prop1, prop2, relation, measure):
            self.prop1 = prop1
            self.prop2 = prop2
            self.relation = relation
            self.measure = measure

class Alignment():
    onto1 = None
    onto2 = None
    cell_list = []
    
    def init(self, uri1, uri2):
        self.onto1 = Graph()
        self.onto1.parse(uri1, format='xml')
        self._bind_prefixes(self.onto1)
        
        self.onto2 = Graph()
        self.onto2.parse(uri2, format='xml')
        self._bind_prefixes(self.onto2)
    
    def add_cell(self, cell):
        self.cell_list.append(cell)

    def _bind_prefixes(self, ontology):
        ontology.bind('owl', 'http://www.w3.org/2002/07/owl#')

    def _get_properties(self, ontology):
        prop_list = []
        base = self._get_base_uri(ontology)
        sparql_result = ontology.query('SELECT DISTINCT ?s WHERE { ?s a owl:ObjectProperty}')
        for s in sparql_result:
            if s not in prop_list and s[0].startswith(base):
                prop_list.append(s)
        
        sparql_result = ontology.query('SELECT DISTINCT ?s WHERE { ?s a owl:DatatypeProperty}')
        for s in sparql_result:
            if s not in prop_list and s[0].startswith(base):
                prop_list.append(s)
        return prop_list
        
    def _get_classes(self, ontology):
        class_list = []
        base = self._get_base_uri(ontology)
        sparql_result = ontology.query('SELECT DISTINCT ?s WHERE {?s a owl:Class}')
        for s in sparql_result:
            if s not in class_list and s[0].startswith(base):
                class_list.append(s)
        return class_list
        
    def _get_entity_name(self, prop):
        if '#' in prop.s:
            root = prop.s.defrag()
            return prop.s.split(root)[1][1:]
        else:
            splitted_uri = prop.s.split('/')
            return splitted_uri[len(splitted_uri) - 1]

    def _get_class_properties(self, class_name, ontology):
        properties = []
        base = self._get_base_uri(ontology)
        sparql_result = ontology.query('SELECT DISTINCT ?s WHERE {<%s> ?s ?o}' % class_name)
        for p in sparql_result:
            if p[0].startswith(base):
                properties.append(p)
        return properties
        
    def _align_local(self, properties1, properties2):
        max_value = 0.0
        moy = 0.0
        prop_matrix = [[0 for x in xrange(len(properties2))] for x in xrange(len(properties1))]
        
        for i in xrange(len(properties1)):
            entity_name1 = self._get_entity_name(properties1[i]).lower()
            for j in xrange(len(properties2)):
                entity_name2 = self._get_entity_name(properties2[j]).lower()
                prop_matrix[i][j] =  1.0 - stringdistances.substring_distance(entity_name1, entity_name2)
                #print entity_name1, entity_name2, 1.0 - stringdistances.substring_distance(entity_name1, entity_name2)
        
        for i in xrange(len(properties1)):
            for j in xrange(len(properties2)):
                if prop_matrix[i][j] > max_value:
                    max_value = prop_matrix[i][j]
            moy = moy + max_value
            max_value = 0.0
        return moy

    def _get_base_uri(self, ontology):
        subjects = set(s for s in ontology.subjects() if isinstance(s, URIRef))
        namespace_dict = {}
        for s in subjects:
            try:
                qname = ontology.qname(s)
                splitted_qname = qname.split(':')
                if len(splitted_qname) == 2:
                    namespace = splitted_qname[0]
                else:
                    namespace = ''
                if namespace in namespace_dict:
                    namespace_dict[namespace] += 1
                else:
                    namespace_dict[namespace] = 1
            except Exception as e:
                print e
                
        #Thanks to @jonlazaro
        namespace = max(namespace_dict.iteritems(), key=operator.itemgetter(1))[0]
        for n in ontology.namespaces():
            if n[0] == namespace:
                return n[1]
                
    def _get_individuals(self, ontology):
        individuals = []
        sparql_result = ontology.query('SELECT DISTINCT ?s WHERE {?s a owl:NamedIndividual .}')
        base = self._get_base_uri(ontology)
        for s in sparql_result:
            if s[0].startswith(base):
                individuals.append(s)
        return individuals
                
class NameAndPropertyAlignment(Alignment):    
    
    def init(self, uri1, uri2):
        #super(NameAndPropertyAlignment, self).init(uri1, uri2)
        Alignment.init(self, uri1, uri2)
        
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
                        prop_matrix[i][j] = pia * stringdistances.substring_distance(entity_name1, entity_name2)
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
                    class_matrix[i][j] = pic * stringdistances.substring_distance(entity_name1, entity_name2)
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
                        cell = AlignmentCell(prop_list1[i], prop_list2[best], '=', 1.0 - max_value)
                        self.add_cell(cell)
                factor = 0.0
                
            for i in xrange(len(class_list1)):
                properties1 = self._get_class_properties(class_list1[i], self.onto1)
                nba1 = len(properties1)
                if nba1 > 0:
                    for j in xrange(len(class_list2)):
                        properties2 = self._get_class_properties(class_list2[j], self.onto2)
                        moy_align_loc = self._align_local(properties1, properties2)
                        if moy_align_loc > 0.7:
                            class_matrix[i][j] = (class_matrix[i][j] + 2 * moy_align_loc) / 3
                           

            for i in xrange(len(class_list1)):
                found = False
                best = 0
                max_value = threshold
                for j in xrange(len(class_list2)):
                    if class_matrix[i][j] < max_value:
                        found = True
                        best = j
                        max_value = class_matrix[i][j]
                if found and max_value < 0.5:
                    cell = AlignmentCell(class_list1[i], class_list2[best], '=', 1.0 - max_value)
                    self.add_cell(cell)
                    
class StringDistAlignment(Alignment):
    
    method = None
    
    def init(self, uri1, uri2):
        #super(NameAndPropertyAlignment, self).init(uri1, uri2)
        Alignment.init(self, uri1, uri2)
        
        
    def _measure(self, class1, class2):
        entity_name1 = self._get_entity_name(class1)
        entity_name2 = self._get_entity_name(class2)
        if entity_name1 == None or entity_name2 == None:
            return 1.0
        #params = (entity_name1.lower(), entity_name2.lower())
        #invoke method
        call = getattr(stringdistances, self.method)
        
        return call(entity_name1.lower(), entity_name2.lower)
        
    def align(self, method='equal_distance'):
        self.method = method
        # Class matrix
        class_list1 = self._get_classes(self.onto1)
        class_dict1 = {}
        count = 0
        for c in class_list1:
            class_dict1[c] = count
            count += 1
        
        class_list2 = self._get_classes(self.onto2)
        class_dict2 = {}
        count = 0
        for c in class_list2:
            class_dict2[c] = count
            count += 1
            
        class_matrix = [[0 for x in xrange(len(class_list2))] for x in xrange(len(class_list1))]
        
        # Prop matrix
        prop_list1 = self._get_properties(self.onto1)
        prop_dict1 = {}
        count = 0
        for p in prop_list1:
            prop_dict1[p] = count
            count += 1
        
        prop_list2 = self._get_properties(self.onto2)
        prop_dict2 = {}
        count = 0
        for p in prop_list2:
            prop_dict2[p] = count
            count += 1
        
        prop_matrix = [[0 for x in xrange(len(prop_list2))] for x in xrange(len(prop_list1))]
        
        # Individuals maxrix
        ind_list1 = self._get_individuals(self.onto1)
        ind_dict1 = {}
        count = 0
        for i in ind_list1:
            try:
                entity_name = self._get_entity_name(i)
                if entity_name != None:
                    ind_dict1[i] = count
                    count += 1
            except:
                pass
                
        ind_list2 = self._get_individuals(self.onto2)
        ind_dict2 = {}
        count = 0
        for i in ind_list2:
            try:
                entity_name = self._get_entity_name(i)
                if entity_name != None:
                    ind_dict2[i] = count
                    count += 1
            except:
                pass
            
        ind_matrix = [[0 for x in xrange(len(ind_list2))] for x in xrange(len(ind_list1))]
        
        # Compute
        
        for class1 in class_list1:
            for class2 in class_list2:
                class_matrix[class_dict1[class1]][class_dict2[class2]] = self._measure(class1, class2)
