from context import Context


class PipelineEngine:
    def __init__(self, pipes, doc):
        self._pipes = pipes
        self._context = Context(doc)

    def process(self):
        return [tuple([pipe.process(self._context, None) for pipe in self._pipes]) for s in self._context.isents()]


