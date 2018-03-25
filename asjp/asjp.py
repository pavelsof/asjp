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
		Init the instance's properties: two dicts mapping IPA symbols to their
		ASJP counterparts and vice versa; and the set of ASJP letters.
		"""
		self.ipa2asjp = {}
		self.asjp2ipa = {}
		self.asjp_letters = set()

	def load(self, path):
		"""
		Populate the instance's properties. The data is expected to be read
		from a file which is parsed as follows:

		- empty lines and lines starting with # are ignored;
		- content lines should consist of tab-separated sub-strings, the first
		  being an IPA symbol, the second its ASJP counterpart, and the
		  presence of the optional third one indicating that the IPA symbol is
		  also the ASJP's counterpart;
		- content lines without a tab are ignored.
		"""
		with open(path, encoding='utf-8') as f:
			for line in map(lambda x: x.strip(), f):
				if not line or line.startswith('#'):
					continue

				line = line.split('\t')
				if len(line) < 2:
					continue

				self.ipa2asjp[line[0].replace('ə͡'[1], '')] = line[1]

				if len(line) > 2:
					self.asjp2ipa[line[1]] = line[0]

		self.asjp_letters = set(self.asjp2ipa.keys())



def ipa2asjp(ipa_seq):
	"""
	Convert an IPA sequence into an ASJP sequence.

	Part of the package's public API.
	"""
	def convert(token):
		output = []
		suffix = ''

		for ix, char in enumerate(token):
			if ipatok.ipa.is_letter(char, strict=False):
				if ix > 1 and ipatok.ipa.is_tie_bar(token[ix-1]):
					output[-1] = chart.ipa2asjp[token[ix-2]+char]
				else:
					output.append(chart.ipa2asjp[char])

			elif char in 'ʰʷʲⁿ':
				suffix = '$' if suffix else '~'
				output.append(chart.ipa2asjp[char])

			elif char == 'ʼ' or char == 'ə̃'[1]:
				output.append(chart.ipa2asjp[char])

			elif char == 'n̪'[1] and ix and token[ix-1] == 'n':
				output[-1] = chart.ipa2asjp['n̪']

		return ''.join(output + [suffix])

	is_str = isinstance(ipa_seq, str)
	if is_str:
		ipa_seq = ipatok.tokenise(ipa_seq, replace=True)

	if not isinstance(ipa_seq, list):
		raise ValueError('')

	asjp_seq = [convert(token) for token in ipa_seq]

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

		if token[-1] in '*"':
			ipa_suffix += {'*': 'ə̃'[1], '"': 'ʼ'}[token[-1]]
			inferred_size = 2
		elif token[-1] in '~$':
			juxtaposed = True
			inferred_size = 3 if token[-1] == '~' else 4

		if inferred_size is None or len(token) != inferred_size:
			raise ValueError('invalid token {}'.format(token))

		token = token[:-1]

	for char in token:
		if juxtaposed and char in 'hwyn':
			output += {'h': 'ʰ', 'w': 'ʷ', 'y': 'ʲ', 'n': 'ⁿ'}[char]
		elif char in chart.asjp2ipa:
			output += chart.asjp2ipa[char]
		else:
			raise ValueError('invalid token {}'.format(token))

	return output + ipa_suffix


def asjp2ipa(asjp_seq):
	"""
	Convert an ASJP sequence (string or list) into an IPA sequence of the same
	type. Raise ValueError if the input is not a valid ASJP sequence and raise
	TypeError if it is not a sequence. Usage:

	>>> asjp2ipa('zEmy~E')
	zamʲa
	>>> asjp2ipa(tokenise('zEmy~E'))
	['z', 'a', 'mʲ', 'a']

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

	>>> tokenise('novE zEmy~E')
	['n', 'o', 'v', 'E', 'z', 'E', 'my~', 'E']

	Part of the package's public API.
	"""
	words = string.split()
	output = []

	for word in words:
		try:
			output.extend(tokenise_word(word))
		except ValueError as err:
			raise ValueError('Cannot tokenise {}: {!s}'.format(word, err))

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
