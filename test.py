from alignapy import NameAndPropertyAlignment, StringDistAlignment, NameEqAlignment

ap = NameEqAlignment()
ap.init('ontologies/aktors.owl', 'ontologies/bibo.owl')

ap.align()

for cell in ap.cell_list:
    print cell.prop1, cell.prop2, cell.measure
