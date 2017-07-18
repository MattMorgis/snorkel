import unittest
import os
os.environ['SNORKELHOME'] = os.path.abspath('.')
from metamap_api import MetaMapAPI


class MetamapAPITest(unittest.TestCase):

    def test_no_concept_in_sentence(self):
        concept = []
        metamap = MetaMapMock(concept)
        metamap_api = MetaMapAPI(metamap)
        sentence = {'text': 'Shoba went on a bike ride this weekend.',
                    'char_offsets':
                        [0, 6, 11, 14, 16, 21, 26, 31, 38],
                    'entity_types':
                        ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O'],
                    'entity_cids':
                        ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O']}

        tagged_sentence = metamap_api.tag(sentence)
        self.assertEqual(tagged_sentence['entity_types'],
                         ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O'])
        self.assertEqual(tagged_sentence['entity_cids'],
                         ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O'])

    def test_singe_one_word_concept_in_sentence(self):
        concept = []
        metamap = MetaMapMock(concept)
        metamap_api = MetaMapAPI(metamap)
        sentence = {'text': 'John has diabetes.',
                    'char_offsets':
                        [0, 5, 9, 17],
                    'entity_types':
                        ['O', 'O', 'O', 'O'],
                    'entity_cids':
                        ['O', 'O', 'O', 'O']}

        tagged_sentence = metamap_api.tag(sentence)
        self.assertEqual(tagged_sentence['entity_types'],
                         ['O', 'O', 'O', 'Disease'])
        self.assertEqual(tagged_sentence['entity_cids'],
                         ['O', 'O', 'O', 'C0011849'])


class MetaMapMock(object):

    def __init__(self, concepts):
        self.concepts = concepts

    def extract_concepts(self,
                         sentences=None,
                         ids=None,
                         filename=None,
                         composite_phrase=4,
                         file_format='sldi',
                         word_sense_disambiguation=True):
        """ Extract concepts from a list of sentences using MetaMap. """
        return (self.concepts, [])


if __name__ == '__main__':
    unittest.main()
