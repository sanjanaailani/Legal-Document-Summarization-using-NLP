
from collections import OrderedDict
import operator
from prettytable import PrettyTable
import re
import saravanan_constants
from saravanan_constants import include_toggled_phrases, include_toggled_pairs
import json
import sys
from nltk.corpus import stopwords
from math import log 


MAX_LENGTH_SUMMARY = 100 
MAX_PERCENT_SUMMARY = 34 

summary_division = {'Introduction':10, 'Context':24, 'Analysis':60, 'Conclusion':6, 'Citation': 0}


mapping_to_CRF = {'FI': "identifying",	'FE': "identifying",
				'I': "establishing", 	'A': "arguments",	'LR': "history",
				'SS': "ratio",			'SP': "arguing",	'SO': "arguments",
				'R': "judgement",		'?': -1
		}


mapping_to_letsum = {'FI': "Introduction",	'FE': "Introduction",
					'I': "Introduction",	'A': "Context", 	'LR': "Context",
					'SS': "Analysis",		'SP': "Analysis",	'SO': "Analysis",
					'R': "Conclusion",		'?': -1
		} 

crf_to_letsum = {"identifying": "Introduction",	"establishing": "Introduction",
				"arguing": "Analysis",			"history": "Context",
				"arguments": "Analysis",		"ratio": "Analysis",
				"judgement": "Conclusion"
		}


cue_phrases = saravanan_constants.categorical_phrases
cue_pairs = saravanan_constants.categorical_pairs

def Mod_LetSum(t):
	'''
		receives a list of sentences, produce categories for each of them
	'''
	label = OrderedDict()
	scores = OrderedDict()
	lines = {}

	length = sum([ len(line.split(' ')) for line in t ])
	print('+++--- Length of document: ', length)
	print('\n+++--- Printing lines and detected cues\n')

	for line in t:
		score = {'Introduction':0, 'Context':0, 'Analysis':0, 'Conclusion':0, 'Citation': 0}
		lines[line] = [i.lower() for i in line.split(' ')]
		words = lines[line]

		found_phrases = []
		for sarav_category in crf_to_letsum:
			letsum_category = crf_to_letsum[sarav_category]
			score[letsum_category] += sum([ 1 for i in cue_phrases[sarav_category] if i in line])
			found_phrases.extend([i for i in cue_phrases[sarav_category] if i in line])

		print(line)
		if found_phrases:
			print(found_phrases)
			print('>', score)
		# print('\n')

		## check for matching pairs
		found_pairs = {}
		for sarav_category in crf_to_letsum:
			letsum_category = crf_to_letsum[sarav_category]
			for pair_start in cue_pairs[sarav_category]:
				found_index = line.find(pair_start)
				if found_index == -1:
					continue
			
				line_onward = line[found_index + len(pair_start) :]
				if any(subsequent_str in line_onward for subsequent_str in cue_pairs[sarav_category][pair_start]):
					score[letsum_category] += 1
					found_pairs[pair_start] = ','.join([subsequent_str for subsequent_str in cue_pairs[sarav_category][pair_start] if subsequent_str in line_onward])

		if found_pairs:
			print(found_pairs)
			print('>>', score)
		print('\n')

		# assign labels based on scores
		if score['Citation'] != 0:
			label[line] = 'Citation'
		else:	# maximal score entity
			if max(score.items(), key=operator.itemgetter(1))[1] == 0:
				label[line] = 'Context (d)'
			else:
				label[line] = max(score.items(), key=operator.itemgetter(1))[0]
		scores[line] = score

	print('\n+++--- Printing label assignment \n')
	pt = PrettyTable()
	pt.field_names = ['#', 'Sentence', 'Intro', 'Context', 'Analysis', 'Conclusion', 'Citation', 'Label']
	c = 0
	for line in t:
		score = scores[line]
		for letsum_category in score:
			if score[letsum_category] == 0:
				score[letsum_category] = '.'
		# print(scores[line]['Introduction'], '\t', scores[line]['Context'], '\t', scores[line]['Analysis'],
			 # '\t', scores[line]['Conclusion'], '\t', scores[line]['Citation'], '\t', label[line])
		pt.add_row([c, line[:50], score['Introduction'], score['Context'], score['Analysis'],
					score['Conclusion'], score['Citation'], label[line]])
		c += 1
	
	print(pt)

	print('\n+++--- Printing classwise text\n')
	category_txt = {'Introduction':'', 'Context':'', 'Analysis':'', 'Conclusion':'', 'Citation': ''}
	for line in scores:
		if label[line] == 'Context (d)':
			category_txt['Context'] += line
		else:
			category_txt[label[line]] += line

	for category in category_txt:
		print('\n\n', category,'\n\n')
		print(category_txt[category])


	txt = ''.join(t)
	stop_words = list( set( stopwords.words('english') ) )
	summary = OrderedDict({'Introduction':'', 'Context':'', 'Citation': '', 'Analysis':'', 'Conclusion':''})
	
	for category in category_txt:
		specific_txt = category_txt[category]
		words = list( filter(None, specific_txt.split(' ') ) )
		
		words_in_summary = int( (MAX_PERCENT_SUMMARY * length * summary_division[category]) / (100 * 100) )

		print('To choose', words_in_summary, ' out of ', len(words), ' words for category', category)
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
			di = sum([1 for i in t if word.lower() in i.lower()]) 
			di = di if di!= 0 else 0.5 
			idf = log( len(t) / di ) 
			tf_idf[word] = tf * idf

		tf_idf_scores = [tf_idf[word] for word in tf_idf]
		tf_idf_scores.sort()
		threshold = tf_idf_scores[words_in_summary - 1] 
		print('Threshold', threshold)
		words_added = 0
		for word in words:
			if tf_idf[word] > threshold:
				summary[category] += word + ' '
				words_added += 1

			if words_added == words_in_summary:
				break

	print('\n+++--- Printing selected sumamry for each category\n')
	for category in summary:
		print('\n\n', category,'\n\n')
		print(summary[category])




def letsum_loader(file):
	# check saravanan's constants	
	include_toggled_phrases(cue_phrases)
	include_toggled_pairs(cue_pairs)

	with open(file, 'r') as f:
		txt = f.readlines()
	if file.split('.')[-1] == 'json':
		tj = json.loads(''.join(txt))
		txt = tj['content']
		t = list(filter(None, txt.split('\n')))
		t = [i.replace('- ', '') for i in t]
		return t

	text = '\n'.join(txt)
	t2 = re.split("S[0-9]+ ", text)
	t2 = list(filter(None, t2)) # remove any empty strings
	t2 = [i.strip('\n').replace('- ', '') for i in t2]
	t = [i.split(' ') for i in t2]
	t = [' '.join(i[1:]) for i in t]

	return t

if __name__ == '__main__':

	file = "unannotated.txt"
	if len(sys.argv) > 1:
		file = sys.argv[1]

	txt = letsum_loader(file)
	Mod_LetSum(txt)