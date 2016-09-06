from abc import ABCMeta, abstractmethod


class Pipe:
    __metaclass__ = ABCMeta

    @abstractmethod
    def process(self, context, passed_tokens):
        return


class AggregatePipe(Pipe):
    def __init__(self, pipes):
        self._pipes = pipes

    def process(self, context, passed_tokens):
        return [pipe.process(context, passed_tokens) for pipe in self._pipes]


class SequencePipe(Pipe):
    def __init__(self, pipes):
        self._pipes = pipes

    def process(self, context, passed_tokens):
        def _process(_pipes, _passed_tokens):
            pipe = _pipes.pop()
            return _process(_pipes(), pipe.process(context, _passed_tokens))

        return _process(list(self._pipes), passed_tokens);