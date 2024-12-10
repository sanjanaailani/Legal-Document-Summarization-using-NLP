

from collections import OrderedDict
import operator
from prettytable import PrettyTable
import re
import json
import sys
from nltk.corpus import stopwords
from math import log 
import html2text
import nltk

from constants import include_toggled_phrases, include_toggled_pairs

MAX_LENGTH_SUMMARY = 100 
MAX_PERCENT_SUMMARY = 34 

summary_division = {'Introduction':10, 'Context':24, 'Analysis':60, 'Conclusion':6, 'Citation': 0}

mapping_to_letsum = {'F': "Introduction", 'I': "Introduction",
					 'A': "Context", 'LR': "Context",
					 'SS': "Analysis", 'SP': "Analysis",
					 'SO': "Conclusion", 'R': "Conclusion"
		}


cue_phrases = formulated_constants.categorical_phrases
cue_pairs = formulated_constants.categorical_pairs
# check saravanan's constants	
include_toggled_phrases(cue_phrases)
include_toggled_pairs(cue_pairs)

def parse_html(file):
	'''
		Return usable case content, as list
	'''
	with open(file, 'r') as f:
		txt = f.read()

	txt=(txt.replace('</?(?!(?:p class=indent)\b)[a-z](?:[^>\"\']|\"[^\"]*\"|\'[^\']*\')*>',''))
	t = html2text.html2text(txt)

	tokenized = nltk.tokenize.sent_tokenize(t)
	start = 0 

	while start < len(tokenized) and 'the judgment was delivered by' not in tokenized[start].lower() :
		start = start + 1

	if start == len(tokenized):
		start = 0
		while 'for educational use only' not in tokenized[start].lower():
			start = start + 1

	text, indices = [], []
	for i in range(start+1,len(tokenized)):
		if 'thomson reuters south asia private limited' in tokenized[i].lower():
			break
		text.append(tokenized[i].replace('\n',' '))
		indices.append(i-start)

	return text, indices

def get_manual_summary(file):
	'''
		Get manual summary from case analysis
	'''
	# rewriting parse_html, as format is different
	with open(file, 'r') as f:
		txt = f.read()
	
	txt=(txt.replace('</?(?!(?:p class=indent)\b)[a-z](?:[^>\"\']|\"[^\"]*\"|\'[^\']*\')*>',''))
	t = html2text.html2text(txt)

	tokenized = nltk.tokenize.sent_tokenize(t)
	t2 = []
	for each in tokenized:
		lines = list( filter( None, each.split('\n') ) )
		t2.extend(lines)

	tokenized = t2
	start = 0 
	
	while start < len(tokenized) and 'summary' not in tokenized[start].lower():
		start = start + 1
	
	# 2010_U_113.html has no summary
	if start == len(tokenized):
		return -1

	text = []
	closing = ['appellate history', 'thomson reuters south asia private limited', 'all cases cited',
				'cases citing this case', 'legislation cited']
	
	summary_str = ' **Summary:** '
	text.append(tokenized[start].replace('\n', ' ')[len(summary_str):])

	for i in range(start+1,len(tokenized)):
		if any(closing_phrase in tokenized[i].lower() for closing_phrase in closing) :
			break
		text.append(tokenized[i].replace('\n',' '))	
	summary = ' '.join(text)
	return summary


def LetSum(file):
	'''
		receives a html file, produce categories for each of them and returns a summary
	'''
	label = OrderedDict()
	scores = OrderedDict()
	lines = {}

	t, _ = parse_html(file)

	length = sum([ len(line.split(' ')) for line in t ])

	for line in t:
		score = {'Introduction':0, 'Context':0, 'Analysis':0, 'Conclusion':0, 'Citation': 0}
		lines[line] = [i.lower() for i in line.split(' ')]
		words = lines[line]

		for category in mapping_to_letsum:
			letsum_category = mapping_to_letsum[category]
			# print('letsum_category', letsum_category, category)
			only_words = [phrase for phrase in cue_phrases[category] if len(phrase.split(' '))== 1]
			score[letsum_category] += sum([1 for phrase in only_words if phrase in words])

			proper_phrases = [phrase for phrase in cue_phrases[category] if phrase not in only_words]			
			score[letsum_category] += sum([ 1 for phrase in proper_phrases if phrase in line ])

		if score['Citation'] != 0:
			label[line] = 'Citation'
		else:	# maximal score entity
			if max(score.items(), key=operator.itemgetter(1))[1] == 0:
				label[line] = 'Context (d)'
			else:
				label[line] = max(score.items(), key=operator.itemgetter(1))[0]
		scores[line] = score


	category_txt = {'Introduction':'', 'Context':'', 'Analysis':'', 'Conclusion':'', 'Citation': ''}
	for line in scores:
		if label[line] == 'Context (d)':
			category_txt['Context'] += line
		else:
			category_txt[label[line]] += line

	txt = ''.join(t)
	stop_words = list( set( stopwords.words('english') ) )
	summary = OrderedDict({'Introduction':'', 'Context':'', 'Citation': '', 'Analysis':'', 'Conclusion':''})
	
	for category in category_txt:
		if category == 'Citation':
			continue
		specific_txt = category_txt[category]
		words = list( filter(None, specific_txt.split(' ') ) )
		
		words_in_summary = int( (MAX_PERCENT_SUMMARY * length * summary_division[category]) / (100 * 100) )
		if words_in_summary == 0:
			continue
		tf_idf = OrderedDict()

		if words_in_summary >= len(words):
			summary[category] = specific_txt
			continue

		for word in words:
			if word in tf_idf:
				continue
			if word.lower() in stop_words:
				tf_idf[word] = 0
				continue
			tf = txt.lower().count( word.lower() )
			di = sum([1 for i in t if word.lower() in i.lower()]) # number of sentences with the word
			di = di if di!= 0 else 0.5 # not really possible, but account for every possibility
			idf = log( len(t) / di ) 
			tf_idf[word] = tf * idf

		tf_idf_scores = [tf_idf[word] for word in tf_idf]
		tf_idf_scores.sort()

		threshold_id = words_in_summary - 1
		if threshold_id > len(tf_idf_scores)-1:
			threshold_id = len(tf_idf_scores) - 1
		# print(threshold_id, len(tf_idf_scores))
		threshold = tf_idf_scores[threshold_id] # words with a score above this used in summary
		# print('Threshold', threshold)
		words_added = 0
		for word in words:
			if tf_idf[word] > threshold:
				summary[category] += word + ' '
				words_added += 1

			# if multiple words have same score, use order of appearance for deciding
			if words_added >= words_in_summary:
				break


	summary_txt = '\n'.join(summary[category] for category in summary)
	return summary_txt


if __name__ == '__main__':

	file = "unannotated.txt"
	if len(sys.argv) > 1:
		file = sys.argv[1]

	LetSum(file)