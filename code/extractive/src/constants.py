categorical_phrases = dict()
categorical_pairs = dict()

categorical_phrases['F'] = [
	'appellant','dated', 'No.', 'State', 'filed', 'Government','registration', 'basis',
	'stated', 'notice', 'period', 'region',
	'January', 'February', 'March','April','May', 'June', 'July', 'August', 'September', 'October', 'November', 'December',

	'the plaintiff', 'the basis', 'basis of', 'Court of', 'stated that', 'filed a', 'was issued', 'the Constitution',
	'the Corporation', 'under Article','plaintiff and', 'show cause',

	'High court of', 'that the said', 'referred to as', 'stated that the', 'In the year', 
]

categorical_pairs['F'] = {	
}

categorical_phrases['I'] = [
	'appeal by',

]

categorical_pairs['I'] = {
}

categorical_phrases['A'] = [
	'service', 'amount', 'value','section', 'goods','credit','license','supplied',
	'recipient', 'country', 'quota', 'contended','contention',

	'under Section', 'terms of', 'counsel for', 'before us', 'charged by', 'is charged', 'free of',

	'charged by the', 'provided by the', 

]

categorical_pairs['A'] = {
}
categorical_phrases['LR'] = [
	'Tribunal', 'defendants', 'Judge', 'Bench','Division', 'trial',

	'held that', 'trial court', 'the parent',

	'that the defendants', 
]

categorical_pairs['LR'] = {
}
categorical_phrases['SS'] = [
	'provisions', 'provision', 'act', 'section', 'chapter', '(', 'explanation', 'commission', 'agent', 'estates',

	'of service', 'subject to', 'deemed to', 'or tenure',

	'as may be', 'the estates of', 

	'the purpose of this', 'in a case where', 'as may be prescribed', 
]

categorical_pairs['SS'] = {
}

categorical_phrases['SP'] = [
	'v', 'Vs', 'vs', 'fact', 'SC', '&', 'conclusion', 'finding', 'SCC', 'S.C.R.', 'SCR',
	'carrying', 'observed',

	'this court', 'of law', 'question of', 'laid down', 'the question', 'was whether', 'decision was', 
	'evidence to', 'this Court', 'a finding',

	'it was held', 'question of fact',
]

categorical_pairs['SP'] = {
}

years = [str(x) for x in list(range(1900, 2100))]
categorical_phrases['SO'] = [
	'Civil', 'Appeal', 

	'Appeal No.',
]

categorical_phrases['SO'].extend(years)
categorical_pairs['SO'] = {
}


categorical_phrases['R'] = [
	'Dismiss', 'dismissed', 'dismissing', 'sustained', 'rejected', 'allowed','passed','case','considered','aside',
	'preliminary','judgement','accordingly', 'amended', 'allow','owed', 'decree',

	'the case', 'the Amending', 'set aside', 'order to',' appeal is', 'the Section', 'execution of', 'Appeal allowed',

	'the part of', 'to the suit', 'of the Court', 

]

categorical_pairs['R'] = {
}


def include_toggled_list(l):
	l_ = list()
	for item in l:
		l_.append(item + '.')
	l += l_
	l_ = list()

	for item in l:
		first_toggled = item[0].lower() if item[0].isupper() else item[0].upper()
		l_.append(first_toggled + item[1:])
	l += l_
	l = list(set(l))


def include_toggled_dict(d):
	
	d_ = dict()
	for key in d:
		first_toggled = key[0].lower() if key[0].isupper() else key[0].upper()
		d_[first_toggled + key[1:]] = d[key]
	d.update(d_)


def include_toggled_phrases(phrases):

	for category in phrases:
		include_toggled_list(phrases[category])


def include_toggled_pairs(pairs):

	total_pairs, c = sum([ len(pairs[category]) for category in pairs ]), 0
	for category in pairs:		
		if category == 'arguing':

			for key in pairs[category]:
				pairs[category][key] = list( set( pairs[category][key] ) )
			pass
		for key in pairs[category]:
			# print ( pairs[category][key] )
			include_toggled_list( pairs[category][key] )
			c += 1

	c = 0
	for category in pairs:
		d2 = {}
		for key in pairs[category]:
			k2 = key[0].upper() if key[0].islower() else key[0].lower()
			d2[k2 + key[1:]] = pairs[category][key]
			c += 1			
		pairs[category].update(d2)

	# make a set
	for category in pairs:
		for key in pairs[category]:
			pairs[category][key] = list( set( pairs[category][key] ) )