class PipelineEngine:
    def __init__(self, pipes, context, requirements=None):
        self._pipes = pipes
        self._context = context
        self._requirements = requirements

    def _verify_requirements(self, t):
        return not self._requirements or all(t[i] for i in self._requirements)

    def process(self):
        result = []

        if not self._pipes:
            return result

        pipes_list = self._pipes if isinstance(self._pipes[0], list) else [self._pipes]

        while self._context.next_sent():
            for pipes in pipes_list:
                t = tuple(pipe.process(self._context, None) for pipe in pipes)
                if self._verify_requirements(t):
                    result.append(t)

        return result


