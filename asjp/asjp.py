import os.path
import unicodedata

import ipatok



"""
Paths to the asjp/data dir and the chart file located there.
"""
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
CHART_FILE = os.path.join(DATA_DIR, 'chart')



class Chart:
	"""
	Object that loads and stores the data from the chart file.
	"""

	def __init__(self):
		"""
		Init the instance's properties: a dict mapping IPA symbols to their
		ASJP counterparts and three dicts for the reverse mapping.
		"""
		self.ipa = {}

		self.asjp_letters = {}
		self.asjp_diacritics = {}
		self.asjp_juxta_letters = {}

	def load(self, path):
		"""
		Populate the instance's properties. The data is expected to be read
		from a file which is parsed as follows:

		- empty lines and lines starting with # are ignored;
		- content lines should consist of tab-separated sub-strings, the first
		  being an IPA symbol, the second its ASJP counterpart, the (optional)
		  third a marker;
		- the marker ✓ indicates that the IPA symbol is also the ASJP's
		  counterpart for the purposes of asjp2ipa conversion;
		- the marker + indicates that the second symbol is an ASJP diacritic;
		- the marker = indicates that the correspondence only applies in the
		  context of an ASJP juxtaposition;
		- content lines without a tab are ignored.
		"""
		with open(path, encoding='utf-8') as f:
			for line in map(lambda x: x.strip(), f):
				if not line or line.startswith('#'):
					continue

				line = line.split('\t')

				if len(line) == 2:
					ipa_symbol, asjp_symbol = line
					flag = ''
				elif len(line) == 3:
					ipa_symbol, asjp_symbol, flag = line
				else:
					continue

				self.ipa[ipa_symbol.replace('ə͡'[1], '')] = asjp_symbol

				if flag == '✓':
					self.asjp_letters[asjp_symbol] = ipa_symbol
				elif flag == '+':
					self.asjp_diacritics[asjp_symbol] = ipa_symbol
				elif flag == '=':
					self.asjp_juxta_letters[asjp_symbol] = ipa_symbol


def convert_ipa_token(token):
	"""
	Convert an IPA token into an ASJP token or raise ValueError if the input
	does not constitute a valid IPA token.

	Helper for ipa2asjp(ipa_seq).
	"""
	output = []

	for ix, char in enumerate(token):
		if ipatok.ipa.is_letter(char, strict=False):
			if ix > 1 and ipatok.ipa.is_tie_bar(token[ix-1]):
				output[-1] = chart.ipa[token[ix-2]+char]
			else:
				output.append(chart.ipa[char])

		elif char == 'n̪'[1] and ix and token[ix-1] == 'n':
			output[-1] = chart.ipa['n̪']

		elif char in chart.ipa:
			output.append(chart.ipa[char])

	if sum([1 for char in output if char in chart.asjp_diacritics]):
		if len(output) != 2:
			raise ValueError('invalid token {}'.format(token))
	else:
		if len(output) == 2:
			output.append('~')
		elif len(output) == 3:
			output.append('$')
		elif len(output) != 1:
			raise ValueError('invalid token {}'.format(token))

	return ''.join(output)


def ipa2asjp(ipa_seq):
	"""
	Convert an IPA sequence (string or list) into an ASJP sequence of the same
	type. Raise ValueError if the input is not a valid IPA sequence and raise
	TypeError if it is not a sequence. Usage:

	>>> ipa2asjp('zɛmʲa')
	'zEmy~a'
	>>> ipa2asjp(['z', 'ɛ', 'mʲ', 'a'])
	['z', 'E', 'my~', 'a']

	Part of the package's public API.
	"""
	is_str = isinstance(ipa_seq, str)
	if is_str:
		ipa_seq = ipatok.tokenise(ipa_seq, replace=True)

	if not isinstance(ipa_seq, list):
		raise TypeError('string or list expected')

	asjp_seq = [convert_ipa_token(token) for token in ipa_seq]

	if is_str:
		return ''.join(asjp_seq)
	else:
		return asjp_seq


def convert_asjp_token(token):
	"""
	Convert an ASJP token into an IPA token or raise ValueError if the input
	does not constitute a valid ASJP token.

	Helper for asjp2ipa(asjp_seq).
	"""
	juxtaposed = False
	ipa_suffix = ''
	output = ''

	if len(token) > 1:
		inferred_size = None

		if token[-1] in chart.asjp_diacritics:
			ipa_suffix += chart.asjp_diacritics[token[-1]]
			inferred_size = 2
		elif token[-1] in '~$':
			juxtaposed = True
			inferred_size = 3 if token[-1] == '~' else 4

		if inferred_size is None or len(token) != inferred_size:
			raise ValueError('invalid token {}'.format(token))

		token = token[:-1]

	for char in token:
		if juxtaposed and char in chart.asjp_juxta_letters:
			output += chart.asjp_juxta_letters[char]
		elif char in chart.asjp_letters:
			output += chart.asjp_letters[char]
		else:
			raise ValueError('invalid token {}'.format(token))

	return output + ipa_suffix


def asjp2ipa(asjp_seq):
	"""
	Convert an ASJP sequence (string or list) into an IPA sequence of the same
	type. Raise ValueError if the input is not a valid ASJP sequence and raise
	TypeError if it is not a sequence. Usage:

	>>> asjp2ipa('zEmy~a')
	'zɛmʲa'
	>>> asjp2ipa(tokenise('zEmy~a'))
	['z', 'ɛ', 'mʲ', 'a']

	Part of the package's public API.
	"""
	is_str = isinstance(asjp_seq, str)
	if is_str:
		asjp_seq = tokenise(asjp_seq)

	if not isinstance(asjp_seq, list):
		raise TypeError('string or list expected')

	ipa_seq = [convert_asjp_token(token) for token in asjp_seq]

	if is_str:
		return ''.join(ipa_seq)
	else:
		return ipa_seq


def tokenise_word(string):
	"""
	Tokenise an ASJP string into a list of tokens or raise ValueError if it
	cannot be unambiguously tokenised. The string is assumed to comprise a
	single word, i.e. it should not contain whitespace chars.

	Helper for tokenise(string).
	"""
	tokens = []

	for ix, char in enumerate(string):
		if char in '~$':
			try:
				for _ in range(1 if char == '~' else 2):
					last_token = tokens.pop()
					tokens[-1] += last_token
				tokens[-1] += char
			except IndexError:
				raise ValueError('ambiguous usage of {} ({})'.format(char, unicodedata.name(char)))

		elif char in '"*':
			try:
				tokens[-1] += char
			except IndexError:
				raise ValueError('word-initial {} ({})'.format(char, unicodedata.name(char)))

		elif char in chart.asjp_letters:
			tokens.append(char)

		else:
			raise ValueError('unknown symbol {} ({})'.format(char, unicodedata.name(char)))

	return tokens


def tokenise(string):
	"""
	Tokenise an ASJP string into a list of tokens or raise ValueError if it
	cannot be unambiguously tokenised. The input may consist of several words,
	i.e. whitespace-separated sub-strings. Usage:

	>>> tokenise('nova zEmy~a')
	['n', 'o', 'v', 'a', 'z', 'E', 'my~', 'a']

	Part of the package's public API.
	"""
	words = string.split()
	output = []

	for word in words:
		try:
			output.extend(tokenise_word(word))
		except ValueError as err:
			raise ValueError('cannot tokenise {}: {!s}'.format(word, err))

	return output


"""
Provide for the alternative spelling.
"""
tokenize = tokenise


"""
Load the chart
"""
chart = Chart()
chart.load(CHART_FILE)
