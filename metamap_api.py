import sys
import os
sys.path.append(os.path.join(os.environ['SNORKELHOME'], 'pymetamap'))
from pymetamap import MetaMap

DISEASE = "Disease"
SYMPTOM = "Symptom"
MetaMap_SYMPTOM = 'sosy'
MetaMap_DISEASE = 'dsyn'


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
            if hasattr(concept, 'semtypes'):
                if MetaMap_SYMPTOM in concept.semtypes:
                    sentence = self.generate_entities(
                        sentence, concept, SYMPTOM)
                elif MetaMap_DISEASE in concept.semtypes:
                    sentence = self.generate_entities(
                        sentence, concept, DISEASE)

        return sentence

    def generate_entities(self, sentence, concept, tag):
        # Ex. "10/8" -> ["10", "8"]
        # Ex. "10/8,11/12" ->
        if ',' in concept.pos_info:
            first_pos = concept.pos_info.split(',')
            position_information = first_pos[0].replace(
                "[", "").replace("]", "").split('/')
        elif ';' in concept.pos_info:
            first_pos = concept.pos_info.split(';')
            position_information = first_pos[0].replace(
                "[", "").replace("]", "").split('/')
        else:
            position_information = concept.pos_info.split('/')
        # MetaMap counts the quotation mark of the sentence
        # starting at index 0
        # while CoreNLP does not, therefore we are left with an
        # off by one error.
        disease_character_start = int(position_information[0]) - 1
        disease_length = int(position_information[1])
        orginial_char_start = disease_character_start

        for index, character_offset in enumerate(sentence['char_offsets']):
            if disease_character_start == character_offset:
                sentence['entity_types'][index] = tag
                if sentence['entity_cids'][index] == 'O':
                    sentence['entity_cids'][index] = concept.cui
                else:
                    sentence['entity_cids'][index] += '|' + concept.cui

                # Check if concept spans multipe words
                if (index + 1) < len(sentence['char_offsets']) - 1:
                    next_char_offset = int(sentence['char_offsets'][index + 1])
                    word_distance = (next_char_offset -
                                     orginial_char_start) - 1
                    if word_distance != disease_length:
                        disease_character_start = next_char_offset

        return sentence
