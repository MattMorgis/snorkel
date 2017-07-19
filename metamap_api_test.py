import unittest
import os
os.environ['SNORKELHOME'] = os.path.abspath('.')
from metamap_api import MetaMapAPI
from pymetamap import ConceptMMI

DISEASE = "Disease"
SYMPTOM = "Symptom"
MetaMap_SYMPTOM = '[sosy]'
MetaMap_DISEASE = '[dsyn]'


class MetamapAPITest(unittest.TestCase):
    """ Test cases for MetaMapAPI class """

    def test_no_concept_in_sentence(self):
        """ Test no diseases or symptoms in a concept. """

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
        sentence = {'text': 'John has diabetes.',
                    'char_offsets':
                        [0, 5, 9, 17],
                    'entity_types':
                        ['O', 'O', 'O', 'O'],
                    'entity_cids':
                        ['O', 'O', 'O', 'O']}
        mm_output = ("index|mm|score|preferred_name|C0011849|[dsyn]|trigger|"
                     "location|10/8|tree_codes")
        concepts = self.buildConcept(mm_output)
        metamap = MetaMapMock(concepts)
        metamap_api = MetaMapAPI(metamap)

        tagged_sentence = metamap_api.tag(sentence)
        self.assertEqual(tagged_sentence['entity_types'],
                         ['O', 'O', DISEASE, 'O'])
        self.assertEqual(tagged_sentence['entity_cids'],
                         ['O', 'O', 'C0011849', 'O'])

    def test_triple_one_word_concept_in_sentence(self):
        # Arrange
        sentence_text = 'John has diabetes which causes hunger and fatigue.'
        sentence = {'text': sentence_text,
                    'char_offsets':
                        [0, 5, 9, 18, 24, 31, 38, 42, 49],
                    'entity_types':
                        ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O'],
                    'entity_cids':
                        ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O']}
        mm_output = ("index|mm|score|preferred_name|C0011849|[dsyn]|trigger"
                     "|location|10/8|tree_codes\nindex|mm|score|preferred_name"
                     "|C0020175|[sosy]|trigger|location|32/6|tree_codes\n"
                     "index|mm|score|preferred_name|C0015672|[sosy]|trigger"
                     "|location|43/7|tree_codes")
        concepts = self.buildConcept(mm_output)
        metamap = MetaMapMock(concepts)
        metamap_api = MetaMapAPI(metamap)

        # Act
        tagged_sentence = metamap_api.tag(sentence)

        # Assert
        self.assertEqual(tagged_sentence['entity_types'],
                         ['O', 'O', DISEASE, 'O', 'O', SYMPTOM, 'O', SYMPTOM, 'O'])
        self.assertEqual(tagged_sentence['entity_cids'],
                         ['O', 'O', 'C0011849', 'O', 'O', 'C0020175', 'O', 'C0015672', 'O'])

    def buildConcept(self, mm_output):
        """ Helper funciton to build mock MetaMap Concept objects.

        Input: Each concept object should be a pipe-deliminated string
            separated by a new line character.

        Ex: index|mm|score|preferred_name|C0011849|[dsyn]|trigger|
            location|10/8|tree_codes \\n <next-concept-string>
        """
        concepts = []
        lines = mm_output.splitlines()
        for line in lines:
            fields = line.split('|')
            concept = ConceptMMI.from_mmi(line)
            concepts.append(concept)
        return concepts


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
