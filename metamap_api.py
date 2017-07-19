import sys
import os
sys.path.append(os.path.join(os.environ['SNORKELHOME'], 'pymetamap'))
from pymetamap import MetaMap

DISEASE = "Disease"
SYMPTOM = "Symptom"
MetaMap_SYMPTOM = '[sosy]'
MetaMap_DISEASE = '[dsyn]'


class MetaMapAPI(object):
    """
    A wrapper used by Snorkel to intereact with the pymetamap package.

    During Snorkel's preprocessing phase, each sentence is passed to this
    metamap interace for diseases and symptoms to be identified.
    """

    def __init__(self, metamap_instance):
        """ Builds an instance of this wrapper interface.

        #param `metamap_instance` -> An instance of the pymetamap
            implementation or a mock.
        """
        self.metamap_instance = metamap_instance

    def tag(self, sentence):
        """ Given a `sentence` from Snorkel, identifies any diseases or symptoms
        and generates the corresponding `entity_types` and `entity_cids`

        Each `sentence` is passed from Snokrel during the pre-processing phase
        to this function. This function will interact with MetaMap to identify
        any diseases or symptoms, and then tag the sentence with the
        corresponding entity: `Disease` or `Symptom`. Addtionally, we identify
        the `cuid` of the medical term. Ex: instances of `diabetes` and
        `diabetes mellitus` will be tagged with the same `cid`.

        """
        sentence_text = [sentence['text']]
        sentence_text[0] = sentence_text[0].encode('ascii', errors='ignore')
        concepts, error = self.metamap_instance.extract_concepts(sentence_text,
                                                                 [1])

        for concept in concepts:
            if concept.semtypes == MetaMap_SYMPTOM:
                sentence = self.generate_entities(sentence, concept, SYMPTOM)
            elif concept.semtypes == MetaMap_DISEASE:
                sentence = self.generate_entities(sentence, concept, DISEASE)
            elif 'dsyn' in concept.semtypes:
                sentence = self.generate_entities(sentence, concept, DISEASE)

        return sentence

    def generate_entities(self, sentence, concept, tag):
        # Ex. "10/8" -> ["10", "8"]
        position_information = concept.pos_info.split('/')
        # MetaMap counts the quotation mark of the sentence
        # starting at index 0
        # while CoreNLP does not, therefore we are left with an
        # off by one error.
        disease_character_start = int(position_information[0]) - 1
        disease_length = int(position_information[1])

        for index, character_offset in enumerate(sentence['char_offsets']):
            if disease_character_start == character_offset:
                sentence['entity_types'][index] = tag
                if sentence['entity_cids'][index] == 'O':
                    sentence['entity_cids'][index] = concept.cui
                else:
                    sentence['entity_cids'][index] += '|' + concept.cui

        return sentence
