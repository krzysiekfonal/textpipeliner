class Context:
    def __init__(self, doc):
        self._sents = []
        self._current_sent_idx = -1
        self._paragraph = self._sents[0:9]
        for s in doc.sents:
            self._sents.append(s)
        self.doc = doc

    def next_sent(self):
        if self._current_sent_idx >= len(self._sents)-1:
            return None

        self._current_sent_idx += 1
        par_low_idx, par_high_idx = self._current_sent_idx - 5, self._current_sent_idx + 5
        if par_low_idx < 0:
            par_high_idx, par_low_idx = par_high_idx-par_low_idx, 0
            self._paragraph = self._sents[par_low_idx:par_high_idx]
        return self.current_sent()

    def isents(self):
        for i in xrange(len(self._sents)):
            yield self.next_sent()

    def current_sent(self):
        return self._sents[self._current_sent_idx]

    def current_paragraph(self):
        return self._paragraph