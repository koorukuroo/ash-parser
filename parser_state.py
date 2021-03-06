# Translation of parser_state.cc from SyntaxNet

from conll_utils import ParsedConllSentence, ParsedConllToken

'''
Handles an individual parsing state within a sentence
'''
class ParserState(object):
    def __init__(self, sentence, feature_maps):
        self.sentence_ = sentence
        self.stack_ = []
        self.head_ = []
        self.label_ = []
        self.num_tokens_ = len(sentence.tokens)
        self.next_ = 0
        self.root_label_ = -1 # always use -1 as <ROOT>
        self.feature_maps = feature_maps

        # keep in sync with head_ and label_
        self.arcs_ = []

        for i in range(self.num_tokens_):
            self.head_.append(-1)
            self.label_.append(self.rootLabel())

    def sentence(self):
        return self.sentence_

    def numTokens(self):
        return self.num_tokens_

    def rootLabel(self):
        return self.root_label_

    def next(self):
        assert self.next_ >= -1
        assert self.next_ <= self.num_tokens_
        return self.next_

    def input(self, offset):
        index = self.next_ + offset
        if index >= -1 and index < self.num_tokens_:
            return index
        else:
            return -2

    def advance(self):
        assert self.next_ < self.num_tokens_
        self.next_ += 1

    def endOfInput(self):
        return self.next_ == self.num_tokens_

    def push(self, index):
        assert len(self.stack_) <= self.num_tokens_
        self.stack_.append(index)

    def pop(self):
        assert len(self.stack_) > 0
        return self.stack_.pop()

    def top(self):
        assert len(self.stack_) > 0
        return self.stack_[-1]

    def stack(self, position):
        if position < 0:
            return -2

        index = len(self.stack_) - 1 - position
        if index < 0:
            return -2
        else:
            return self.stack_[index]

    def stackSize(self):
        return len(self.stack_)

    def stackEmpty(self):
        return len(self.stack_) == 0

    def head(self, index):
        assert index >= -1
        assert index < self.num_tokens_
        if index == -1:
            return -1
        else:
            return self.head_[index]

    def label(self, index):
        assert index >= -1
        assert index < self.num_tokens_
        if index == -1:
            return self.rootLabel()
        else:
            return self.label_[index]

    def parent(self, index, n):
        assert index >= -1
        assert index < self.num_tokens_
        while (n > 0):
            n -= 1
            index = self.head(index)

        return index

    def leftmostChild(self, index, n):
        assert index >= -1
        assert index < self.num_tokens_
        while (n > 0):
            n -= 1
            i = -1
            while i < index:
                if self.head(i) == index:
                    break
                i += 1
            if i == index:
                return -2
            index = i
        return index

    def rightmostChild(self, index, n):
        assert index >= -1
        assert index < self.num_tokens_
        while (n > 0):
            n -= 1
            i = self.num_tokens_ - 1
            while i > index:
                if self.head(i) == index:
                    break
                i -= 1
            if i == index:
                return -2
            index = i
        return index

    def leftSibling(self, index, n):
        assert index >= -1
        assert index < self.num_tokens_
        if index == -1 and n > 0:
            return -2
        i = index
        while n > 0:
            i -= 1
            if i == -1:
                return -2
            if self.head(i) == self.head(index):
                n -= 1
        return i

    def rightSibling(self, index, n):
        assert index >= -1
        assert index < self.num_tokens_
        i = index
        while n > 0:
            i += 1
            if i == self.num_tokens_:
                return -2
            if self.head(i) == self.head(index):
                n -= 1
        return i

    def addArc(self, index, head, label):
        assert index >= 0
        assert index < self.num_tokens_
        self.head_[index] = head
        self.label_[index] = label
        self.arcs_.append((head, label, index))

    def goldHead(self, index):
        assert index >= -1
        assert index < self.num_tokens_
        if index == -1:
            return -1
        offset = 0
        gold_head = self.getToken(index).HEAD
        if gold_head == -1:
            return -1
        else:
            return gold_head - offset

    def goldLabel(self, index):
        assert index >= -1
        assert index < self.num_tokens_
        if index == -1:
            return self.rootLabel()

        try:
            gold_label = self.feature_maps['label'] \
                .valueToIndex(self.getToken(index).DEPREL)

            assert gold_label >= 0

            if gold_label > self.feature_maps['label'].lastBaseValue:
                # if strange value, match SyntaxNet behavior
                return self.rootLabel()
            else:
                return gold_label
        except:
            # if strange value, match SyntaxNet behavior
            return self.rootLabel()

    def getToken(self, index):
        if index == -1:
            return ParsedConllToken()
        return self.sentence_.tokens[index]

    ## TODO: what about index==-1??
    def hasHead(self, index):
        assert index >= 0
        assert index < self.num_tokens_
        return self.head_[index] != -1

    # TODO: cache or something?
    # finds dependents
    def goldDeps(self, index):
        deps = {}
        for dep in range(0, self.num_tokens):
            head = self.goldHead(dep)
            #if dep != head: # in case of root
            if head not in deps:
                deps[head] = []
            deps[head].append(dep)
        return deps
