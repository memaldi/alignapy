from rdflib import Graph
from rdflib.term import URIRef
from nltk.corpus import wordnet as wn
from nltk.tokenize import wordpunct_tokenize
from requests.exceptions import MissingSchema
import stringdistances
import operator
import requests
import uuid

class UriNotFound(Exception):
    def __init__(self, uri):
        Exception.__init__(self, 'URI <%s> not found!' % uri)
        self.uri = uri
        
class IncorrectMimeType(Exception):
    def __init__(self, uri):
        Exception.__init__(self, 'Incorrect Mime Type in <%s>' % uri)
        self.uri = uri
        
class UnsupportedContent(Exception):
    def __init__(self, uri):
        Exception.__init__(self, 'Unsupported content in <%s>' % uri)
        self.uri = uri
        
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
    
    def __init__(self):
        cell_list = []
    
    def init(self, uri1, uri2):
        try:
            file1, content = self._get_ontology(uri1)
        except UriNotFound as e:
            raise e
        except KeyError as e:
            content = 'application/rdf+xml'
            
        self.onto1 = Graph()
        
        if 'text/html' in content:
            raise UnsupportedContent(uri1)  
        elif 'application/rdf+xml' in content or 'application/rdf\\+xml' in content or 'application/owl+xml' in content:
            try:
                self.onto1.parse(file1, format='xml')
            except:
                try:
                    self.onto2.parse(file2, format='turtle')
                except:
                    raise IncorrectMimeType(uri2)
        elif 'text/plain' in content:
            try:
                self.onto1.parse(file1, format='nt')
            except:
                try:
                    self.onto1.parse(file1, format='turtle')
                except:
                    try:
                        self.onto1.parse(file1, format='xml')
                    except:
                        raise IncorrectMimeType(uri1)
        elif 'text/turtle':
            try:
                self.onto1.parse(file1, format='turtle')
            except:
                raise IncorrectMimeType(uri1)
        else:
            try:
                self.onto2.parse(file2, format='xml')
            except:
                raise UnsupportedContent(uri1)
        
        
        self._bind_prefixes(self.onto1)
        try:
            file2, content = self._get_ontology(uri2)
        except UriNotFound as e:
            raise e
        except KeyError as e:
            content = 'application/rdf+xml'
        self.onto2 = Graph()
        
        if 'text/html' in content:
            raise UnsupportedContent(uri2)  
        elif 'application/rdf+xml' in content or 'application/rdf\\+xml' in content or 'application/owl+xml' in content:
            try:
                self.onto2.parse(file2, format='xml')
            except:
                try:
                    self.onto2.parse(file2, format='turtle')
                except:
                    raise IncorrectMimeType(uri2)
        elif 'text/plain' in content:
            try:
                self.onto2.parse(file2, format='nt')
            except:
                try:
                    self.onto2.parse(file2, format='turtle')
                except:
                    try:
                        self.onto2.parse(file2, format='xml')
                    except:
                        raise IncorrectMimeType(uri2)
        elif 'text/turtle':
            try:
                self.onto2.parse(file2, format='turtle')
            except:
                raise IncorrectMimeType(uri2)
        else:
            try:
                self.onto2.parse(file2, format='xml')
            except:
                raise UnsupportedContent(uri2)

        self._bind_prefixes(self.onto2)
    
    def add_cell(self, cell):
        self.cell_list.append(cell)

    def _get_ontology(self, url, timeout=30):
        headers={'Accept': 'application/rdf+xml'}
        try:
            r = requests.get(url, headers=headers, timeout=timeout)
        except MissingSchema as e:
            raise UriNotFound(url)
        except Exception as e:
            raise UriNotFound(url)
        if r.status_code == 404:
            raise UriNotFound(url)
        filename = '/tmp/' + str(uuid.uuid4()) + '.owl'
        f = open(filename, 'w')
        f.write(r.text.encode('utf-8'))
        f.close()
        try:
            content_type = r.headers['content-type']
        except KeyError as e:
            raise e
        #print content_type
        return filename, content_type
       

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
        if len(prop_list) + len(sparql_result) == 0:
            sparql_result = ontology.query('SELECT DISTINCT ?s WHERE { ?s a rdf:Property}') 
        for s in sparql_result:
            if s not in prop_list and s[0].startswith(base):
                prop_list.append(s)
        return prop_list
        
    def _get_classes(self, ontology):
        class_list = []
        base = self._get_base_uri(ontology)
        sparql_result = ontology.query('SELECT DISTINCT ?s WHERE {?s a owl:Class}')
        if len(sparql_result) == 0:
            sparql_result = ontology.query('SELECT DISTINCT ?s WHERE {?s a rdfs:Class}')
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
                pass
                
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
                
        
    def _populate_matrix(self, list1, list2, pia):
        matrix = [[0 for x in xrange(len(list2))] for x in xrange(len(list1))]
        for i, item1 in zip(xrange(len(list1)), list1):
            entity_name1 = self._get_entity_name(item1)
            if entity_name1 != None:
                entity_name1 = entity_name1.lower()
            
            for j, item2 in zip(xrange(len(list2)), list2):
                entity_name2 = self._get_entity_name(item2)
                if entity_name2 != None:
                    entity_name2 = entity_name2.lower()
                
                if entity_name1 != None or entity_name2 != None:                
                    matrix[i][j] = pia * stringdistances.substring_distance(entity_name1, entity_name2)
                else:
                    matrix[i][j] = 1.0
        return matrix
        
                
class NameAndPropertyAlignment(Alignment):    
    
    def __init__(self):
        self.cell_list = []
    
    def _make_alignment(self, list1, list2, matrix, threshold, epsillon, factor):
        while factor > epsillon:
            for i in xrange(len(list1)):
                found = False
                best = 0
                max_value = threshold
                for j in xrange(len(list2)):
                    if matrix[i][j] < max_value:                 
                        found = True
                        best = j
                        max_value = matrix[i][j]
                if found and max_value < 0.5:
                    cell = AlignmentCell(list1[i], list2[best], '=', 1.0 - max_value)
                    self.add_cell(cell)
            factor = 0.0
            
    def _make_local_alignment(self, list1, list2, matrix):
        for i in xrange(len(list1)):
            properties1 = self._get_class_properties(list1[i], self.onto1)
            nba1 = len(properties1)
            if nba1 > 0:
                for j in xrange(len(list2)):
                    properties2 = self._get_class_properties(list2[j], self.onto2)
                    moy_align_loc = self._align_local(properties1, properties2)
                    if moy_align_loc > 0.7:
                        matrix[i][j] = (matrix[i][j] + 2 * moy_align_loc) / 3
        return matrix
                        
    def init(self, uri1, uri2):
        #super(NameAndPropertyAlignment, self).init(uri1, uri2)
        Alignment.init(self, uri1, uri2)
        
    def align(self, threshold=1.0, pia=1.0, pic=0.5, epsillon=0.05):
        #Parameters
        #pia = 1.0 # relation weight for name
        #pic = 0.5 # class weigth for name
        #epsillon = 0.05 # stoping condition 
        #threshold = 1.0 # threshold above which distances are too high
        factor = 1.0
        
        if self.onto1 != None and self.onto2 != None:            
            # Create property lists and matrix
            prop_list1 = self._get_properties(self.onto1)
            prop_list2 = self._get_properties(self.onto2)
            prop_matrix = self._populate_matrix(prop_list1, prop_list2, pia)
             
            # Create class lists and matrix
            class_list1 = self._get_classes(self.onto1)
            class_list2 = self._get_classes(self.onto2)
            class_matrix = self._populate_matrix(class_list1, class_list2, pic)
                
            self._make_alignment(prop_list1, prop_list2, prop_matrix, threshold, epsillon, factor)
            class_matrix = self._make_local_alignment(class_list1, class_list2, class_matrix)
            self._make_alignment(class_list1, class_list2, class_matrix, threshold, epsillon, factor)
                    
class StringDistAlignment(Alignment):
    
    def __init__(self):
        self.cell_list = []
    
    method = None
    
    def init(self, uri1, uri2):
        #super(NameAndPropertyAlignment, self).init(uri1, uri2)
        Alignment.init(self, uri1, uri2)
      
    def _measure(self, object1, object2):
        entity_name1 = self._get_entity_name(object1)
        entity_name2 = self._get_entity_name(object2)
        if entity_name1 == None or entity_name2 == None:
            return 1.0
        #params = (entity_name1.lower(), entity_name2.lower())
        #invoke method
        call = getattr(stringdistances, self.method)(entity_name1.lower(), entity_name2.lower())
        return call
        
    def align(self, method='equal_distance', threshold=0.0):
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
        
        # Compute distances on classes
        for class1 in class_list1:
            for class2 in class_list2:
                class_matrix[class_dict1[class1]][class_dict2[class2]] = self._measure(class1, class2)
        
        # Compute distances on individuals
        for ind1 in ind_list1:
            for ind2 in ind_list2:
                ind_matrix[ind_dict1[ind1]][ind_dict2[ind2]] = self._measure(ind1, ind2)
                
        # Compute distances on properties
        for prop1 in prop_list1:
            for prop2 in prop_list2:
                prop_matrix[prop_dict1[prop1]][prop_dict2[prop2]] = self._measure(prop1, prop2)
                
        # Extract
        #threshold = 0.0
        max_value = 0.0
        found = False
        val = 0.0
        
        # Extract for properties
        for prop1 in prop_list1:
            found = False
            max_value = threshold
            prop2 = None
            for current in prop_list2:
                val = 1.0 - prop_matrix[prop_dict1[prop1]][prop_dict2[current]]
                if val > max_value:
                    found = True
                    max_value = val
                    prop2 = current
            if found:
                cell = AlignmentCell(prop1, prop2, '=', max_value)
                self.add_cell(cell)
        
        # Extract for classes
        for class1 in class_list1:
            found = False
            max_value = threshold
            class2 = None
            for current in class_list2:
                val = 1.0 - class_matrix[class_dict1[class1]][class_dict2[current]]
                if val > max_value:
                    found = True
                    max_value = val
                    class2 = current
            if found:
                cell = AlignmentCell(class1, class2, '=', max_value)
                self.add_cell(cell)
                
        # Extract for individuals
        for ind1 in ind_list1:
            found = False
            max_value = threshold
            ind2 = None
            for current in ind_list2:
                val = 1.0 - ind_matrix[ind_dict1[ind1]][ind_dict2[current]]
                if val > max_value:
                    found = True
                    max_value = val
                    ind2 = current
            if found:
                cell = AlignmentCell(ind1, ind2, '=', max_value)
                self.add_cell(cell)
              
                
class NameEqAlignment(StringDistAlignment):

    def __init__(self):
        self.cell_list = []

    def init(self, uri1, uri2):
        StringDistAlignment.init(self, uri1, uri2)
    
    def align(self, threshold=0.0):
        StringDistAlignment.align(self,  method='equal_distance', threshold=0.0)
        
        
class EditDistNameAlignment(StringDistAlignment):

    def __init__(self):
        self.cell_list = []

    def init(self, uri1, uri2):
        StringDistAlignment.init(self, uri1, uri2)
    
    def align(self, threshold=0.0):
        StringDistAlignment.align(self,  method='levenshtein_distance', threshold=0.0)
        
        
class SMOANameAlignment(StringDistAlignment):
    
    def __init__(self):
        self.cell_list = []
    
    def init(self, uri1, uri2):
        StringDistAlignment.init(self, uri1, uri2)
        
    def align(self, threshold=0.0):
        StringDistAlignment.align(self, method='smoa_distance', threshold=0.0)
        

class SubsDistNameAlignment(StringDistAlignment):

    def __init__(self):
        self.cell_list = []

    def init(self, uri1, uri2):
        StringDistAlignment.init(self, uri1, uri2)
        
    def align(self, threshold=0.0):
        StringDistAlignment.align(self, method='substring_distance', threshold=0.0)


class JWNLAlignment(Alignment):

    def __init__(self):
        self.cell_list = []

    def _basic_synonym_distance(self, string1, string2):
        string1 = string1.lower()
        string2 = string2.lower()
        
        dist_subs = stringdistances.substring_distance(string1, string2)
        synsets = wn.synsets(string1, wn.NOUN)
        if len(synsets) == 0:
            tokens = wordpunct_tokenize(string1)
            for token in tokens:
                synsets = wn.synsets(string1, wn.NOUN)
                if len(synsets) > 0:
                    break
        if len(synsets) > 0:
            for synset in synsets:
                for lemma in synset.lemmas:
                    dist = stringdistances.substring_distance(lemma.name, string2)
                    if (dist < dist_subs):
                        dist_subs = dist
        return dist_subs
        

    def _measure(self, class1, class2):
        entity_name1 = self._get_entity_name(class1)
        entity_name2 = self._get_entity_name(class2)
        
        if entity_name1 == None or entity_name2 == None:
            return 1
        
        if self.method == 'basic_syn_dist':
            return self._basic_synonym_distance(entity_name1, entity_name2)
        
    def init(self, uri1, uri2):
        Alignment.init(self, uri1, uri2)
        
    def align(self, method='basic_syn_dist', threshold=0.0):
        self.method = method
        # Create properties lists and matrix
        prop_list1 = self._get_properties(self.onto1)
        prop_list2 = self._get_properties(self.onto2)
        prop_matrix = [[0 for x in xrange(len(prop_list2))] for x in xrange(len(prop_list1))]
         
        # Create class lists and matrix
        class_list1 = self._get_classes(self.onto1)
        class_list2 = self._get_classes(self.onto2)
        class_matrix = [[0 for x in xrange(len(class_list2))] for x in xrange(len(class_list1))]
        
        # Create individuals lists and matrix
        ind_list1 = self._get_individuals(self.onto1)
        ind_list2 = self._get_individuals(self.onto2)
        ind_matrix = [[0 for x in xrange(len(ind_list2))] for x in xrange(len(ind_list1))]

        for i, class1 in zip(xrange(len(class_list1)), class_list1):
            for j, class2 in zip(xrange(len(class_list2)), class_list2):
                value = 1.0 - self._measure(class1, class2)
                class_matrix[i][j] = value
                if value > threshold:
                    cell = AlignmentCell(class1, class2, '=', value)
                    self.add_cell(cell)
                
        for i, prop1 in zip(xrange(len(prop_list1)), prop_list1):
            for j, prop2 in zip(xrange(len(prop_list2)), prop_list2):
                value = 1.0 - self._measure(prop1, prop2)
                prop_matrix[i][j] = value
                if value > threshold:
                    cell = AlignmentCell(prop1, prop2, '=', value)
                    self.add_cell(cell)
                
        for i, ind1 in zip(xrange(len(ind_list1)), ind_list1):
            for j, ind2 in zip(xrange(len(ind_list2)), ind_list2):
                value = 1.0 - self._measure(ind1, ind2)
                ind_matrix[i][j] = value
                if value > threshold:
                    cell = AlignmentCell(ind1, ind2, '=', value)
                    self.add_cell(cell)
         

'''class ClassStructAlignment(Alignment):
    
    def init(self, uri1, uri2):
        Alignment.init(self, uri1, uri2)

    def align(self):
        pic1 = 0.5
        pic2 = 0.5
        
        # Create class lists and matrix
        class_list1 = self._get_classes(self.onto1)
        class_list2 = self._get_classes(self.onto2)
        class_matrix = [[0 for x in xrange(len(class_list2))] for x in xrange(len(class_list1))]
        
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
        
        for i in xrange(len(class_list1)):
                properties1 = self._get_class_properties(class_list1[i], self.onto1)
                nba1 = len(properties1)
                if nba1 > 0:
                    for j in xrange(len(class_list2)):
                        properties2 = self._get_class_properties(class_list2[j], self.onto2)
                        nba2 = len(properties2)
                        attsum = 0.0
                        for prop1 in properties1:
'''
