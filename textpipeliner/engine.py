from context import Context


class PipelineEngine:
    def __init__(self, pipes, doc, requirements=None):
        self._pipes = pipes
        self._context = Context(doc)
        self._requirements = requirements

    def _verify_requirements(self, t):
        return not self._requirements or all(t[i] for i in self._requirements)

    def process(self):
        result = []
        while self._context.next_sent():
            t = tuple(pipe.process(self._context, None) for pipe in self._pipes)
            if self._verify_requirements(t):
                result.append(t)

        return result


