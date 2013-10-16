from alignapy import NameAndPropertyAlignment

ap = NameAndPropertyAlignment()
ap.init('http://www.aktors.org/ontology/portal', 'http://purl.org/ontology/bibo/')
ap.align()
