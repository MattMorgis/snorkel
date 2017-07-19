""" Example Snorkel project that uses MetaMap
    to identify diseases and symptoms as entities.
"""

import sys
import os
sys.path.append(os.path.join(os.environ['SNORKELHOME'], 'pymetamap'))
from snorkel import SnorkelSession
from snorkel.parser import XMLMultiDocPreprocessor
from snorkel.parser import CorpusParser
from metamap_api import MetaMapAPI
from snorkel.models import Document, Sentence
from pymetamap import MetaMap

data_file_path = 'tutorials/cdr/data/CDR.BioC.small.xml'

snorkel_session = SnorkelSession()

# print sys.path
doc_preprocessor = XMLMultiDocPreprocessor(
    path=data_file_path,
    doc='.//document',
    text='.//passage/text/text()',
    id='.//id/text()'
)

metamap_instance = MetaMap.get_instance(
    '/Users/morgism/Developer/Python/metamap/public_mm/bin/metamap16')
metamap_api = MetaMapAPI(metamap_instance)
corpus_parser = CorpusParser(fn=metamap_api.tag)
corpus_parser.apply(list(doc_preprocessor))

print("Documents:", snorkel_session.query(Document).count())
print("Sentences:", snorkel_session.query(Sentence).count())
