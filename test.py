from alignapy import NameAndPropertyAlignment

ap = NameAndPropertyAlignment()
ap.init('ontologies/aktors.owl', 'ontologies/bibo.owl')

ap.align()
alignment = ap.alignment

for cell in alignment.cell_list:
    print cell.prop1, cell.prop2, cell.measure
