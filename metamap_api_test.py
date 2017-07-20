import unittest
import os
os.environ['SNORKELHOME'] = os.path.abspath('.')
from metamap_api import MetaMapAPI
from pymetamap import ConceptMMI

DISEASE = "Disease"
SYMPTOM = "Symptom"


class MetamapAPITest(unittest.TestCase):
    """ Test cases for MetaMapAPI class """

    def test_no_concept_in_sentence(self):
        """ Test no diseases or symptoms in a concept. """
        # Arrange
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

        # Act
        tagged_sentence = metamap_api.tag(sentence)

        # Assert
        self.assertEqual(tagged_sentence['entity_types'],
                         ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O'])
        self.assertEqual(tagged_sentence['entity_cids'],
                         ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O'])

    def test_singe_one_word_concept_in_sentence(self):
        # Arrange
        sentence = {'text': 'John has diabetes today.',
                    'char_offsets':
                        [0, 5, 9, 18, 23],
                    'entity_types':
                        ['O', 'O', 'O', 'O', 'O'],
                    'entity_cids':
                        ['O', 'O', 'O', 'O', 'O']}
        mm_output = ("index|mm|score|preferred_name|C0011849|[dsyn]|trigger|"
                     "location|10/8|tree_codes")
        concepts = self.buildConcept(mm_output)
        metamap = MetaMapMock(concepts)
        metamap_api = MetaMapAPI(metamap)

        # Act
        tagged_sentence = metamap_api.tag(sentence)

        # Assert
        self.assertEqual(tagged_sentence['entity_types'],
                         ['O', 'O', DISEASE, 'O', 'O'])
        self.assertEqual(tagged_sentence['entity_cids'],
                         ['O', 'O', 'C0011849', 'O', 'O'])

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

    def test_multiple_concepts_same_word_in_sentence(self):
        # Arrange
        sentence_text = 'Sarah has cold.'
        sentence = {'text': sentence_text,
                    'char_offsets':
                        [0, 6, 10, 14],
                    'entity_types':
                        ['O', 'O', 'O', 'O'],
                    'entity_cids':
                        ['O', 'O', 'O', 'O']}
        mm_output = ("index|mm|score|preferred_name|C0011849|[dsyn]|trigger"
                     "|location|11/4|tree_codes\nindex|mm|score|preferred_name"
                     "|C0020175|[dsyn]|trigger|location|11/4|tree_codes\n"
                     "index|mm|score|preferred_name|C0015672|[phsf]|trigger"
                     "|location|11/4|tree_codes")

        concepts = self.buildConcept(mm_output)
        metamap = MetaMapMock(concepts)
        metamap_api = MetaMapAPI(metamap)

        # Act
        tagged_sentence = metamap_api.tag(sentence)

        # Assert
        self.assertEqual(tagged_sentence['entity_types'],
                         ['O', 'O', DISEASE, 'O'])
        self.assertEqual(tagged_sentence['entity_cids'],
                         ['O', 'O', 'C0011849|C0020175', 'O'])

    def test_multiple_disease_semtypes_for_concept_in_sentence(self):
        # Arrange
        sentence_text = 'Sarah has hypertension.'
        sentence = {'text': sentence_text,
                    'char_offsets':
                        [0, 6, 10, 22],
                    'entity_types':
                        ['O', 'O', 'O', 'O'],
                    'entity_cids':
                        ['O', 'O', 'O', 'O']}
        mm_output = ("index|mm|score|preferred_name|C0011849|[dsyn,fndg]|trigger"
                     "|location|11/12|tree_codes")

        concepts = self.buildConcept(mm_output)
        metamap = MetaMapMock(concepts)
        metamap_api = MetaMapAPI(metamap)

        # Act
        tagged_sentence = metamap_api.tag(sentence)

        # Assert
        self.assertEqual(tagged_sentence['entity_types'],
                         ['O', 'O', DISEASE, 'O'])
        self.assertEqual(tagged_sentence['entity_cids'],
                         ['O', 'O', 'C0011849', 'O'])

    def test_multiple_symptom_semtypes_for_concept_in_sentence(self):
        # Arrange
        sentence_text = 'Sarah is fatigued and hungry today.'
        sentence = {'text': sentence_text,
                    'char_offsets':
                        [0, 6, 9, 18, 22, 29, 34],
                    'entity_types':
                        ['O', 'O', 'O', 'O', 'O', 'O', 'O'],
                    'entity_cids':
                        ['O', 'O', 'O', 'O', 'O', 'O', 'O']}
        mm_output = ("index|mm|score|preferred_name|C0015672|[sosy,fndg]|trigger"
                     "|location|10/8|tree_codes\nindex|mm|score|preferred_name|"
                     "C0020175|[sosy,fndg]|trigger|location|23/6|tree_codes")

        concepts = self.buildConcept(mm_output)
        metamap = MetaMapMock(concepts)
        metamap_api = MetaMapAPI(metamap)

        # Act
        tagged_sentence = metamap_api.tag(sentence)

        # Assert
        self.assertEqual(tagged_sentence['entity_types'],
                         ['O', 'O', SYMPTOM, 'O', SYMPTOM, 'O', 'O'])
        self.assertEqual(tagged_sentence['entity_cids'],
                         ['O', 'O', 'C0015672', 'O', 'C0020175', 'O', 'O'])

    def test_one_concept_spanning_multiple_words_in_sentence(self):
        # Arrange
        sentence_text = 'John has a common cold today.'
        sentence = {'text': sentence_text,
                    'char_offsets':
                        [0, 5, 9, 11, 18, 23, 28],
                    'entity_types':
                        ['O', 'O', 'O', 'O', 'O', 'O', 'O'],
                    'entity_cids':
                        ['O', 'O', 'O', 'O', 'O', 'O', 'O']}
        mm_output = ("index|mm|score|preferred_name|C0009443|[dsyn]|"
                     "trigger|location|12/11|tree_codes")

        concepts = self.buildConcept(mm_output)
        metamap = MetaMapMock(concepts)
        metamap_api = MetaMapAPI(metamap)

        # Act
        tagged_sentence = metamap_api.tag(sentence)

        # Assert
        self.assertEqual(tagged_sentence['entity_types'],
                         ['O', 'O', 'O', DISEASE, DISEASE, 'O', 'O'])
        self.assertEqual(tagged_sentence['entity_cids'],
                         ['O', 'O', 'O', 'C0009443', 'C0009443', 'O', 'O'])

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
