import nltk
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters
from nltk import FreqDist
import math
import re
class sentence:
    def __init__(self):
        self.sentence = None
        self.tokens = []
        self.weights = {}
        # Sentence , paragraph and document, total are the keys

class paragraph:
    def __init__(self):
        self.paragraph = None
        self.tokens = []
        self.weights = {}
        self.quota = 0
        # It holds two keys words and total
        # total is a dict with keys words and sentences
        self.sentences = []
        self.sentences_keep = []
class fractal:
    def __init__(self, text):
        self.paragraphs = []
        self.weights = FreqDist(nltk.word_tokenize(text))
        self.sentence_keep = []
        self.sentences_sorted = []

class fractalSummary:
    def __init__(self,text, quota):
        self.text = text
        #print self.text
        self.quota = quota
        self.summary = []
        self.fractal= fractal(text)
        self.paragraphs = text.split('\n\n')
        self.s_weight = 0 # Total sentence weight [0,1]
        self.p_weight = 0 # Toral paragraph weight [0,1]
        self.pindex = 0 # Paragrah index
        self.ptotal = len(self.paragraphs)
        self.sindex = 0 # Sentence index
        self.stotal = 0 # Total sentences
        self.np_weight = 0
        self.ns_weight = 0
    def calculate_relative_frequence(self, sentence_token, weights):
        frequency = {}
        for each_word, freq in weights.items():
            if each_word in sentence_token:
                frequency[each_word] = freq
        return frequency
    def fractal_representation(self):
        punkt_param = PunktParameters()
        for each_paragraph in self.paragraphs:
            buffer_p = paragraph()
            buffer_p.paragraph = each_paragraph
            buffer_p.tokens = nltk.word_tokenize(each_paragraph)
            buffer_p.weights['words'] = FreqDist(nltk.word_tokenize(each_paragraph))
            buffer_p.weights['total'] = {'words':0, 'sentences':0}    
            punkt_param.abbrev_types = set(['dr', 'vs', 'mr', 'mrs', 'prof', 'inc'])
            sentence_splitter = PunktSentenceTokenizer(punkt_param)
            sentences = sentence_splitter.tokenize(each_paragraph)
            for each_sentence in sentences:
                self.stotal += 1
                buffer_s = sentence()
                buffer_s.sentence = each_sentence
                buffer_s.tokens = nltk.word_tokenize(each_sentence)
                if len(buffer_s.tokens) > 0:
                    buffer_s.weights['sentence'] = FreqDist(nltk.word_tokenize(each_sentence))
                    buffer_s.weights['paragraph'] = self.calculate_relative_frequence(buffer_s.tokens, buffer_p.weights['words'])
                    buffer_s.weights['document'] = self.calculate_relative_frequence(buffer_s.tokens, self.fractal.weights)
                    buffer_s.weights['total'] = {}
                    buffer_s.weights['total']['paragraph'] = sum(buffer_s.weights['paragraph'].values())
                    buffer_s.weights['total']['document'] = sum(buffer_s.weights['document'].values())
                    self.s_weight += buffer_s.weights['total']['document']
                    buffer_p.weights['total']['sentences'] += buffer_s.weights['total']['document']
                    buffer_p.sentences.append(buffer_s)
            buffer_p.weights['total']['words'] = sum(buffer_p.weights['words'].values())
            self.fractal.paragraphs.append(buffer_p)
            self.pindex += 1
    def normalize(self):
        quota_sum = 0
        for each_paragraph in self.fractal.paragraphs:
            each_paragraph.weights['total']['normalized'] = each_paragraph.weights['total']['sentences'] / float(self.s_weight)
            self.np_weight += each_paragraph.weights['total']['normalized']
            each_paragraph.quota = round(self.quota * each_paragraph.weights['total']['normalized'])
            quota_sum += each_paragraph.quota
            sentences_sorted = []
            index = 0
            for each_sentence in each_paragraph.sentences:
                each_sentence.weights['total']['sentence_normalized'] = each_sentence.weights['total']['document']/float(self.s_weight)
                self.ns_weight += each_sentence.weights['total']['sentence_normalized']
                sentences_sorted.append({'weight' : each_sentence.weights['total']['sentence_normalized'], 'text': each_sentence.sentence, 'index': index})
                index += 1
            sentences_sorted.sort(key=lambda x:x['weight'], reverse=True)
            # keep only our quotas of sentences, sorted by index asc
            sentences_sorted = sentences_sorted[:int(each_paragraph.quota)]
            sentences_sorted.sort(key=lambda x:x['index'])
            for each_sen in sentences_sorted:
                each_paragraph.sentences_keep.append(each_sen['text'])
            if len(each_paragraph.sentences_keep) > 0:
                for each_sen in each_paragraph.sentences_keep:
                    self.summary.append(each_sen.strip())
def main():
    f = open("news.txt","r")
    fs = fractalSummary(f.read(), 6)
    fs.fractal_representation()
    fs.normalize()
    print "summary"
    for eac_sen in fs.summary:
        print eac_sen

if __name__ == "__main__":
    main()