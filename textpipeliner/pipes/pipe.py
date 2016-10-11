from abc import ABCMeta, abstractmethod
from grammaregex import find_tokens, match_tree


class Pipe:
    __metaclass__ = ABCMeta

    @abstractmethod
    def process(self, context, passed_tokens=None):
        return []


class AggregatePipe(Pipe):
    def __init__(self, pipes, with_flattening=True):
        self._pipes = pipes
        self._with_flattening = with_flattening

    def process(self, context, passed_tokens):
        agg_result = [pipe.process(context, passed_tokens) for pipe in self._pipes]
        return agg_result if not self._with_flattening else [item for sublist in agg_result for item in sublist]


class SequencePipe(Pipe):
    def __init__(self, pipes):
        self._pipes = pipes

    def process(self, context, passed_tokens=None):
        def _process(_pipes, _passed_tokens):
            pipe = _pipes.pop(0)
            result = pipe.process(context, _passed_tokens)
            return result if not _pipes else _process(_pipes, result)

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
        return self._fun(context, passed_tokens)


class FindTokensPipe(Pipe):
    def __init__(self, pattern, precondition=None):
        self._pattern = pattern
        self._precondition = precondition

    def process(self, context, passed_tokens=None):
        return \
            find_tokens(context.current_sent(), self._pattern) \
            if not self._precondition or match_tree(context.current_sent(), self._precondition) else []


class NamedEntityFilterPipe(Pipe):
    def __init__(self, named_entity_type=None):
        self._named_entity_type = named_entity_type

    def process(self, context, passed_tokens=None):
        return [x for x in passed_tokens
                if (x.ent_iob_ == 'B' or x.ent_iob_ == 'I') and
                (not self._named_entity_type or x.ent_type_ == self._named_entity_type)]


class NamedEntityExtractorPipe(Pipe):
    def process(self, context, passed_tokens=None):
        def _extract_named_entity(token):
            ne = [token]
            if token.ent_iob_ == 'I':
                i = token.i-1
                while context.doc[i].ent_iob_ != 'O':
                    ne.insert(0, context.doc[i])
                    i -= 1
            i = token.i+1
            while context.doc[i].ent_iob_ == 'I':
                ne.append(context.doc[i])
                i += 1
            return ne
        result = []
        for x in passed_tokens:
            if x.ent_iob_ == 'B' or x.ent_iob_ == 'I':
                ne = _extract_named_entity(x)
                if not any(ne[0].i == _ne[0].i for _ne in result):
                    result.append(ne)

        return result[0] if len(result) == 1 else result


class UnfoldConjPipe(Pipe):
    def process(self, context, passed_tokens=None):
        if passed_tokens:
            result = [passed_tokens[0]]
            current = passed_tokens[0]
            while current:
                for t in current.children:
                    if t.dep_ == "conj":
                        result.append(t)
                        current = t
                        break
                else:
                    current = None
            return result
        return []
