import os.path
import unicodedata

import ipatok



"""
Paths to the asjp/data dir and the map file located there.
"""
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
CHART_FILE = os.path.join(DATA_DIR, 'chart')



class Chart:
	"""
	"""

	def __init__(self):
		"""
		"""
		self.ipa2asjp = {}
		self.asjp2ipa = {}
		self.asjp_letters = set()

	def load(self, path):
		"""
		Populate the instance's dicts and set.
		"""
		with open(path, encoding='utf-8') as f:
			for line in map(lambda x: x.strip(), f):
				if not line or line.startswith('#'):
					continue

				line = line.split('\t')
				if len(line) < 2:
					continue

				self.ipa2asjp[line[0]] = line[1]

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


def asjp2ipa(asjp_seq):
	"""
	Convert an ASJP sequence into an IPA sequence.

	Part of the package's public API.
	"""
	pass


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
