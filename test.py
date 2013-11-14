from alignapy import NameAndPropertyAlignment, StringDistAlignment, NameEqAlignment, EditDistNameAlignment, SMOANameAlignment, SubsDistNameAlignment, JWNLAlignment

ap = JWNLAlignment()
ap.init('http://purl.org/dc/terms/', 'http://aktors.org/ontology/portal')

try:
    ap.align(threshold=0.7)
except Exception as e:
    pass
print len(ap.cell_list)
for cell in ap.cell_list:
    print cell.prop1, cell.prop2, cell.measure
