import unittest
from textpipeliner import *
from textpipeliner.pipes import *
import spacy

# _sentence will be used throughout the all tests as it is time-consuming to create it.
# The fact of time-consumption is also reason for keeping all tests in single module file
_sentence = None


def setUpModule():
    nlp = spacy.load("en")
    global _doc
    _doc = nlp(u"Mrs. Robinson graduated from the Wharton School of the University of Pennsylvania in 1980 and 1982.")


class PipesProcessingTestCase(unittest.TestCase):
    @staticmethod
    def _pass_tokens_fun(ctx, passed_tokens):
            return passed_tokens

    @staticmethod
    def _reduce_token_fun(ctx, passed_tokens):
        result = list(passed_tokens)
        result.pop()
        return result

    def setUp(self):
        self.passed_tokens = [_doc[1], _doc[2], _doc[4]]  # ["Robinson", "graduated", "the"]
        self.ctx = Context(_doc)

    def test_generic_pipe(self):
        pipe = GenericPipe(self._pass_tokens_fun)
        self.assertEqual(self.passed_tokens, pipe.process(self.ctx, self.passed_tokens))

    def test_find_tokens_pipe(self):
        pipe = FindTokensPipe("VBD/prep/*")
        expected = [_doc[3], _doc[12]]  # ["from", "in"]
        self.assertEqual(expected, pipe.process(self.ctx))

    def test_named_entity_filter_pipe(self):
        pipe = NamedEntityFilterPipe()
        expected = [_doc[1], _doc[4]]  # ["Robinson", "the"]
        self.assertEqual(expected, pipe.process(self.ctx, self.passed_tokens))

        pipe = NamedEntityFilterPipe("PERSON")
        expected = [_doc[1]]  # ["Robinson"]
        self.assertEqual(expected, pipe.process(self.ctx, self.passed_tokens))

    def test_named_entity_extractor_pipe(self):
        pipe = NamedEntityExtractorPipe()
        # [["Robinson"], ["the", "Wharton", "School", "of", "the", "University", "of", "Pennsylvania"]]
        expected = [[_doc[1]], [_doc[4], _doc[5], _doc[6], _doc[7], _doc[8], _doc[9], _doc[10], _doc[11]]]
        self.assertEqual(expected, pipe.process(self.ctx, self.passed_tokens))

    def test_unfold_conj_pipe(self):
        pipe = UnfoldConjPipe()
        expected = [_doc[13], _doc[15]] # ["1980", "1982"]
        self.assertEqual(expected, pipe.process(self.ctx, [_doc[13]]))

    def test_aggregate_pipe(self):
        pipe1 = GenericPipe(self._pass_tokens_fun)
        pipe2 = GenericPipe(self._pass_tokens_fun)

        pipe = AggregatePipe([pipe1, pipe2])
        expected = [_doc[1], _doc[2], _doc[4], _doc[1], _doc[2], _doc[4]]
        self.assertEqual(expected, pipe.process(self.ctx, self.passed_tokens))

        pipe = AggregatePipe([pipe1, pipe2], False)
        expected = [[_doc[1], _doc[2], _doc[4]], [_doc[1], _doc[2], _doc[4]]]
        self.assertEqual(expected, pipe.process(self.ctx, self.passed_tokens))

    def test_sequence_pipe(self):
        pipe1 = GenericPipe(self._reduce_token_fun)
        pipe2 = GenericPipe(self._reduce_token_fun)

        pipe = SequencePipe([pipe1, pipe2])
        expected = [_doc[1]]  # ["Robinson"]
        self.assertEqual(expected, pipe.process(self.ctx, self.passed_tokens))

    def test_any_pipe(self):
        pipe1 = NamedEntityFilterPipe("ORG")
        pipe2 = NamedEntityFilterPipe("PERSON")

        pipe = AnyPipe([pipe1, pipe2])
        expected = [_doc[4]]  # ["the"]
        self.assertEqual(expected, pipe.process(self.ctx, self.passed_tokens))

        pipe = AnyPipe([pipe2, pipe1])
        expected = [_doc[1]]  # ["Robinson"]
        self.assertEqual(expected, pipe.process(self.ctx, self.passed_tokens))


class PipelineEngineTestCase(unittest.TestCase):
    def setUp(self):
        self.ctx = Context(_doc)

    def test_process_without_requirements(self):
        pipes_structure = [SequencePipe([FindTokensPipe("VBD/nsubj/*"),
                                        AggregatePipe([NamedEntityFilterPipe("PERSON"), NamedEntityFilterPipe("ORG")]),
                                        NamedEntityExtractorPipe()]),
                           FindTokensPipe("VBD"),
                           SequencePipe([FindTokensPipe("VBD/**/*/pobj/NNP"),
                                        AggregatePipe([NamedEntityFilterPipe("PERSON"), NamedEntityFilterPipe("ORG")]),
                                        NamedEntityExtractorPipe()])]

        engine = PipelineEngine(pipes_structure, _doc)
        expected = [([_doc[1]], [_doc[2]], [_doc[4], _doc[5], _doc[6], _doc[7], _doc[8], _doc[9], _doc[10], _doc[11]])]
        self.assertEqual(expected, engine.process())

    def test_process_with_requirements(self):
        pipes_structure = [SequencePipe([FindTokensPipe("VBD/nsubj/*"),
                                        AggregatePipe([NamedEntityFilterPipe("PERSON"), NamedEntityFilterPipe("ORG")]),
                                        NamedEntityExtractorPipe()]),
                           FindTokensPipe("NNP"),
                           SequencePipe([FindTokensPipe("VBD/**/*/pobj/NNP"),
                                        AggregatePipe([NamedEntityFilterPipe("PERSON"), NamedEntityFilterPipe("ORG")]),
                                        NamedEntityExtractorPipe()])]

        engine = PipelineEngine(pipes_structure, _doc, [1])
        expected = []
        self.assertEqual(expected, engine.process())

