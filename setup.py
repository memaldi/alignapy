from setuptools import setup, find_packages
setup(
    name = "Alignapy",
    version = "0.1",
    packages = find_packages(),
    namespace_packages=['swanalyzer'],
    install_requires=[
                'rdflib>=4.0.1',
                'nltk>=2.0',
                'requests>=2.0.0',
    ],
    author = "Mikel Emaldi",
    author_email = "m.emaldi@deusto.es",
    description = "Python port of some features of Alignapi (http://alignapi.gforge.inria.fr/)",
    license = "LGPL",
    keywords = "rdf ontology matching linked data semantic web",
    url = "https://github.com/memaldi/alignapy",   # project home page, if any
)

