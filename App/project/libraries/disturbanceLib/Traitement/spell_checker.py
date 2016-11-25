import re, collections
import os.path
import unicodedata

def list_to_string(l):
    """
       Transforme une liste de token sous forme d'une string (phrase)
    """
    s = ""
    for w in l:
        if len(s) == 0:
            s = w
        else:
            s = s + " " + w
    return s

class SpellChecker(object):
    """
    Correcteur orthographique
    """
    alphabet = 'abcdefghijklmnopqrstuvwxyz'

    def __init__(self):
        path_learn_dirname = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(path_learn_dirname, 'lexique/dictionnaire.txt'), 'rb') as f:
            text = f.read()
        self.NWORDS = self._train(self._words(text.lower()))
        
                
    def _words(self, text):
        return re.findall('[a-z]+', text.lower())


    def _train(self, features):
        model = collections.defaultdict(lambda: 1)
        for f in features:
            model[f] += 1
        return model
            
            
    def _edits1(self, word):
        s = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes    = [a + b[1:] for a, b in s if b]
        transposes = [a + b[1] + b[0] + b[2:] for a, b in s if len(b)>1]
        replaces   = [a + c + b[1:] for a, b in s for c in self.alphabet if b]
        inserts    = [a + c + b     for a, b in s for c in self.alphabet]
        return set(deletes + transposes + replaces + inserts)


    def _known_edits2(self, word):
        return set(e2 for e1 in self._edits1(word) for e2 in self._edits1(e1) if e2 in self.NWORDS)


    def _known(self, words):
        return set(w for w in words if w in self.NWORDS)


    def correct(self, word):

        candidates = self._known([word]) or self._known(self._edits1(word)) or self._known_edits2(word) or [word]        
        return max(candidates, key=self.NWORDS.get)
        # unicodedata.normalize('NFD', max(candidates, key=self.NWORDS.get)).encode('ascii', 'ignore')
        


    def corrections(self, text): 
        return unicode(list_to_string(map(lambda m: self.correct(m), text.split())))
