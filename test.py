from alignapy import AlignmentProcess

ap = AlignmentProcess()
ap.init('http://www.aktors.org/ontology/portal', 'http://purl.org/ontology/bibo/')
ap.align()
