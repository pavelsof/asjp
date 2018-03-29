from unittest import TestCase

from hypothesis.strategies import composite, lists, sampled_from
from hypothesis import assume, given

from asjp.asjp import chart
from asjp import ipa2asjp, asjp2ipa, tokenise



ASJP_JUXTA_LETTERS = ''.join(sorted(chart.asjp_juxta_letters.keys()))
ASJP_LETTERS = ''.join(sorted(chart.asjp_letters.keys()))



@composite
def asjp_tokens(draw):
	"""
	Composite strategy that generates a non-empty ASJP token.
	"""
	suffix = draw(sampled_from('_"*~$'))

	if suffix in '_"*':
		token = draw(sampled_from(ASJP_LETTERS))
		if suffix != '_':
			token += suffix

	else:
		token = draw(sampled_from(ASJP_LETTERS))
		token += draw(sampled_from(ASJP_LETTERS))

		if suffix == '$':
			token += draw(sampled_from(ASJP_LETTERS))

		assume(any([char not in ASJP_JUXTA_LETTERS for char in token]))

		token += suffix

	return token



class ApiTestCase(TestCase):

	def test_ipa2asjp_strings(self):
		"""
		IPA-compliant strings should be correctly converted to ASJP.

		The IPA strings are sourced from NorthEuraLex (bul, che, deu, swe),
		their ASJP counterparts are derived manually.
		"""
		self.assertEqual(ipa2asjp(''), '')

		self.assertEqual(ipa2asjp('sɫɤnt͡sɛ'), 'sloncE')
		self.assertEqual(ipa2asjp('zvɛzda'), 'zvEzda')
		self.assertEqual(ipa2asjp('zɛmʲa'), 'zEmy~a')
		self.assertEqual(ipa2asjp('ɔɡɤn'), 'ogon')
		self.assertEqual(ipa2asjp('javʲa sɛ'), 'yavy~a sE')

		self.assertEqual(ipa2asjp('motː'), 'mot')
		self.assertEqual(ipa2asjp('t͡ʃʼenɪɡ'), 'C"enig')
		self.assertEqual(ipa2asjp('bu͡ʊqʼ'), 'buq"')
		self.assertEqual(ipa2asjp('tʼu͡ʊlɡ'), 't"ulg')
		self.assertEqual(ipa2asjp('bu͡ʊt͡s'), 'buc')

		self.assertEqual(ipa2asjp('zɔnə'), 'zon3')
		self.assertEqual(ipa2asjp('vasɐ'), 'vasa')
		self.assertEqual(ipa2asjp('ʃtaɪ̯n'), 'Stain')
		self.assertEqual(ipa2asjp('ɛɐ̯də'), 'Ead3')
		self.assertEqual(ipa2asjp('fɔʏ̯ɐ'), 'foia')

		self.assertEqual(ipa2asjp('ɧɪnː'), 'Sx~in')
		self.assertEqual(ipa2asjp('ɧæːɳa'), 'Sx~Ena')
		self.assertEqual(ipa2asjp('ɔtːɧɪlɪɡ'), 'otSx~ilig')

	def test_ipa2asjp_lists(self):
		"""
		IPA-compliant tokens should be correctly converted to ASJP tokens.
		"""
		self.assertEqual(ipa2asjp([]), [])

		self.assertEqual(ipa2asjp(['s', 'ɫ', 'ɤ', 'n', 't͡s', 'ɛ']), ['s', 'l', 'o', 'n', 'c', 'E'])
		self.assertEqual(ipa2asjp(['z', 'ɛ', 'mʲ', 'a']), ['z', 'E', 'my~', 'a'])

		self.assertEqual(ipa2asjp(['t͡ʃʼ', 'e', 'n', 'ɪ', 'ɡ']), ['C"', 'e', 'n', 'i', 'g'])
		self.assertEqual(ipa2asjp(['b', 'u͡ʊ', 'qʼ']), ['b', 'u', 'q"'])

		self.assertEqual(ipa2asjp(['ʃ', 't', 'a', 'ɪ̯', 'n']), ['S', 't', 'a', 'i', 'n'])
		self.assertEqual(ipa2asjp(['ʃ', 't', 'a͡ɪ̯', 'n']), ['S', 't', 'a', 'n'])

		self.assertEqual(ipa2asjp(['ɧ', 'ɪ', 'nː']), ['Sx~', 'i', 'n'])
		self.assertEqual(ipa2asjp(['ɔ', 'tː', 'ɧ', 'ɪ', 'l', 'ɪ', 'ɡ']), ['o', 't', 'Sx~', 'i', 'l', 'i', 'g'])

	def test_ipa2asjp_errors(self):
		"""
		Non-IPA sequences should raise ValueError and non-sequences should
		raise TypeError.
		"""
		for item in [None, True, 42]:
			with self.assertRaises(TypeError):
				ipa2asjp(item)

		for item in ['zEmy~a', 'павел']:
			with self.assertRaises(ValueError):
				ipa2asjp(item)

		for item in [['z', 'E', 'my~', 'a'], ['п']]:
			with self.assertRaises(ValueError):
				ipa2asjp(item)

	def test_asjp2ipa_strings(self):
		"""
		ASJP strings should be converted into IPA-compliant strings.
		"""
		self.assertEqual(asjp2ipa(''), '')
		self.assertEqual(asjp2ipa('sloncE'), 'slont͡sɛ')
		self.assertEqual(asjp2ipa('zvEzda'), 'zvɛzda')
		self.assertEqual(asjp2ipa('zEmy~a'), 'zɛmʲa')
		self.assertEqual(asjp2ipa('yavy~a sE'), 'javʲa sɛ')

	def test_asjp2ipa_lists(self):
		"""
		ASJP tokens should be converted into IPA-compliant tokens.
		"""
		self.assertEqual(asjp2ipa([]), [])
		self.assertEqual(asjp2ipa(['s', 'l', 'o', 'n', 'c', 'E']), ['s', 'l', 'o', 'n', 't͡s', 'ɛ'])
		self.assertEqual(asjp2ipa(['z', 'E', 'my~', 'a']), ['z', 'ɛ', 'mʲ', 'a'])

	def test_asjp2ipa_errors(self):
		"""
		Non-ASJP sequences should raise ValueError and non-sequences should
		raise TypeError.
		"""
		for item in [None, True, 42]:
			with self.assertRaises(TypeError):
				asjp2ipa(item)

		for item in ['zɛmʲa', 'павел']:
			with self.assertRaises(ValueError):
				asjp2ipa(item)

		for item in [['z', 'ɛ', 'mʲ', 'a'], ['п']]:
			with self.assertRaises(ValueError):
				asjp2ipa(item)

	@given(lists(asjp_tokens()))
	def test_asjp_ipa_asjp(self, tokens):
		"""
		Tokens generated by asjp_tokens() should be correctly recovered after
		being converted to IPA.
		"""
		self.assertEqual(ipa2asjp(asjp2ipa(tokens)), tokens)

	def test_tokenise(self):
		"""
		ASJP strings should be correctly tokenised.
		"""
		self.assertEqual(tokenise(''), [])
		self.assertEqual(tokenise('nova zEmy~a'), ['n', 'o', 'v', 'a', 'z', 'E', 'my~', 'a'])
		self.assertEqual(tokenise('a*kw~ndy$k"'), ['a*', 'kw~', 'ndy$', 'k"'])

	def test_tokenise_errors(self):
		"""
		Non-ASJP strings should raise ValueError and non-strings should raise
		TypeError.
		"""
		for item in [None, True, 42]:
			with self.assertRaises(TypeError):
				tokenise(item)

		for item in ['*a', '"p', 'a~', 'aa$', 'a~$']:
			with self.assertRaises(ValueError):
				tokenise(item)

	@given(lists(asjp_tokens()))
	def test_tokenise_generated(self, tokens):
		"""
		Concatenated tokens generated by asjp_tokens() should be correctly
		tokenised back.
		"""
		self.assertEqual(tokenise(''.join(tokens)), tokens)
