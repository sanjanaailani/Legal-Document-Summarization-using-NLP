import os
import nltk
import operator
from nltk.corpus import stopwords
from collections import OrderedDict
from prettytable import PrettyTable
import sys

CATEGORIES_FOLDER = 'categories'
MIN_THRESHOLD = 5 

stop_words = set(stopwords.words('english'))
stop_words.update(['.', ',', '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}']) # remove it if you need punctuation 
print(stop_words)

def filteredStopWords(l):
	return [i for i in list(filter(None, l.split(" ") ) ) if i.lower() not in stop_words]


def words(l):
	return [i for i in list(filter(None, l.split(" ") ) ) ]


def set_count(l):
	ls = list(set(l))
	lc = dict()
	for ls in l:
		if ls not in lc:
			lc[ls] = 0
		lc[ls] += 1
	return list(set(l)), lc


def print_top_key_count(l, n=11):
	if n > len(l):
		n = len(l)
	for s in l[:n]:
		print( s[0], '\t', s[1] )


def print_top_key_count_combined(uni, bi, tri, quadri, n=11):
	if n > len(quadri):
		n = len(quadri)
	for a, b, c, d in zip(uni[:n], bi[:n], tri[:n], quadri[:n]):
		print( a[0], '\t', a[1], '\t', ' ', '\t',
			   b[0], '\t', b[1], '\t', ' ', '\t',
			   c[0], '\t', c[1], '\t', ' ', '\t',
			   d[0], '\t', d[1], '\t'			   )


def get_ngrams(file):
	category = file.split('.')[0]
	# print(category,'\n\n')
	with open(file, 'r') as f:
		txt = f.readlines()
	txt = [t.replace('\n', '') for t in txt]
	# how to distinguish full stop and I.P.C ?
	# txt = [t.replace('.', ' .').replace('\n', '') for t in txt]
	t2     = [[word for word in line.split()] for line in txt]
	uni = []
	for sentence_words in t2:
		filtered = filteredStopWords(' '.join(sentence_words))
		uni = uni + filtered


	bi     = [b for l in txt for b in zip(filteredStopWords(l)[:-1], filteredStopWords(l)[1:])]
	tri    = [t for l in txt for t in zip(filteredStopWords(l)[:-2], filteredStopWords(l)[1:-1], filteredStopWords(l)[2:])]
	quadri = [q for l in txt for q in zip(filteredStopWords(l)[:-3], filteredStopWords(l)[1:-2], filteredStopWords(l)[2:-1], filteredStopWords(l)[3:])]
	

	bi, tri, quadri = [], [], []
	for l in txt:
		# only add n-grams which are not purely stopwords
		for b in zip(words(l)[:-1], words(l)[1:]):
			if any(word not in stop_words for word in b):
				bi.append(b)
		
		for t in zip(words(l)[:-2], words(l)[1:-1], words(l)[2:]):
			if any(word not in stop_words for word in t):
				tri.append(t)
		
		for q in zip(words(l)[:-3], words(l)[1:-2], words(l)[2:-1], words(l)[3:]):
			if any(word not in stop_words for word in q):
				quadri.append(q)
	

	
	unis, unic = set_count(uni)
	bis, bic = set_count(bi)
	tris, tric = set_count(tri)
	quadris, quadric = set_count(quadri)

	# sorted in reverse order of frequency
	sorted_uni = sorted(unic.items(), key= lambda kv: kv[1], reverse=True)
	sorted_bi = sorted(bic.items(), key= lambda kv: kv[1], reverse=True)
	sorted_tri = sorted(tric.items(), key= lambda kv: kv[1], reverse=True)
	sorted_quadri = sorted(quadric.items(), key= lambda kv: kv[1], reverse=True)

	
	return sorted_uni, sorted_bi, sorted_tri, sorted_quadri


def optimize_ngrams(ngram):
	
	for file in os.listdir(CATEGORIES_FOLDER):
		category = file.split('.')[0]
		print('\n\n', category)
		thisgram = ngram[category]

		# check how often each ngram appears in other categories
		pt = PrettyTable()
		header = ['Phrase', category, 'Othermax']
		for other_file in sorted(os.listdir(CATEGORIES_FOLDER)):
			if other_file == file:
				continue
			header.append( other_file.split('.')[0] )
		pt.field_names = header

		i, length = 1, len(thisgram) 
		for pair in thisgram:
			phrase = pair[0]
			# will be tuple for n > 1
			if not isinstance(phrase, str):
				phrase = ' '.join(word for word in phrase)
			
			with open(CATEGORIES_FOLDER + '/' + file, 'r') as f:
				txt = f.read()
			freq = txt.count(phrase)
			if freq <= MIN_THRESHOLD:
				continue


			row = [phrase, freq]
			i += 1
			counts = {}
			for other_file in sorted(os.listdir(CATEGORIES_FOLDER)):
				category2 = other_file.split('.')[0]
				if other_file == file:
					continue
				with open(CATEGORIES_FOLDER + '/' + other_file, 'r') as f:
					txt = f.read()
				
				counts[category2] = txt.count(phrase)
				row.append(counts[category2])

			m = max(counts.items(), key=operator.itemgetter(1))[1]
			row.insert(2, m)
			if row[1] > m:
				pt.add_row(row)

		print(pt)
	exit(0)


def ngram_loop():

	if(len(sys.argv) > 1):
		n = int(sys.argv[1])
	
	categories = []
	for file in os.listdir(CATEGORIES_FOLDER):
		if file.startswith('?'):
			continue
		category = file.split('.')[0]
		categories.append(category)

	uni, bi, tri, quadri = {}, {}, {}, {}
	for file in os.listdir(CATEGORIES_FOLDER):
		category = file.split('.')[0]
		u, b, t, q = get_ngrams(CATEGORIES_FOLDER + '/' + file)
		uni[category], bi[category], tri[category], quadri[category] = u, b, t, q

	if n==1:
		optimize_ngrams(uni)
	elif n==2:
		optimize_ngrams(bi)
	elif n==3:
		optimize_ngrams(tri)
	else:
		optimize_ngrams(quadri)


if __name__ == '__main__':
	ngram_loop()