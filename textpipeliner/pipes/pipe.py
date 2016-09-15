from abc import ABCMeta, abstractmethod
from grammaregex import find_tokens, match_tree


class Pipe:
    __metaclass__ = ABCMeta

    @abstractmethod
    def process(self, context, passed_tokens=None):
        return []


class AggregatePipe(Pipe):
    def __init__(self, pipes):
        self._pipes = pipes

    def process(self, context, passed_tokens):
        return [pipe.process(context, passed_tokens) for pipe in self._pipes]


class SequencePipe(Pipe):
    def __init__(self, pipes):
        self._pipes = pipes

    def process(self, context, passed_tokens=None):
        def _process(_pipes, _passed_tokens):
            pipe = _pipes.pop()
            return _process(_pipes(), pipe.process(context, _passed_tokens))

        return _process(list(self._pipes), passed_tokens);


class AnyPipe(Pipe):
    def __init__(self, pipes):
        self._pipes = pipes

    def process(self, context, passed_tokens=None):
        for pipe in self._pipes:
            result = pipe.process(context, passed_tokens)
            if result:
                return result

        return []


class GenericPipe(Pipe):
    def __init__(self, fun):
        self._fun = fun

    def process(self, context, passed_tokens=None):
        return self._fun(passed_tokens)


class FindTokensPipe(Pipe):
    def __init__(self, pattern, precondition=None):
        self._pattern = pattern
        self._precondition = precondition

    def process(self, context, passed_tokens=None):
        return \
            find_tokens(context.current_sent(), self._pattern) \
                if self._precondition and match_tree(context.current_sent(), self._precondition) else []


class NamedEntityFilterPipe(Pipe):
    def __init__(self, named_entity_type=None):
        self._named_entity_type = named_entity_type

    def process(self, context, passed_tokens=None):
        return [x for x in passed_tokens \
                if x.ent_iob_ == 'B' and (not self._named_entity_type or x.ent_type_ == self._named_entity_type)]


class NamedEntityExtractorPipe(Pipe):
    def process(self, context, passed_tokens=None):
        def _extract_named_entity(token):
            result, i = [token], token.i+1
            while context.doc[i].ent_iob_ == 'I':
                result += context.doc[i]
        return [_extract_named_entity(x) for x in passed_tokens if x.ent_iob_ == 'B']