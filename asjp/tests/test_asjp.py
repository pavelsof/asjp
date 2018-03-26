from unittest import TestCase

from asjp import ipa2asjp, asjp2ipa, tokenise



class ApiTestCase(TestCase):

	def test_ipa2asjp(self):
		"""
		IPA-compliant strings should be correctly converted to ASJP.

		The IPA strings are sourced from NorthEuraLex (bul, deu, eng), their
		ASJP counterparts are derived manually.
		"""
		self.assertEqual(ipa2asjp('sɫɤnt͡sɛ'), 'sloncE')
		self.assertEqual(ipa2asjp('zvɛzda'), 'zvEzda')
		self.assertEqual(ipa2asjp('vɔda'), 'voda')
		self.assertEqual(ipa2asjp('kamɤk'), 'kamok')
		self.assertEqual(ipa2asjp('zɛmʲa'), 'zEmy~a')
		self.assertEqual(ipa2asjp('ɔɡɤn'), 'ogon')

		self.assertEqual(ipa2asjp('zɔnə'), 'zon3')
		self.assertEqual(ipa2asjp('ʃtɐn'), 'Stan')
		self.assertEqual(ipa2asjp('vasɐ'), 'vasa')
		self.assertEqual(ipa2asjp('ʃtaɪ̯n'), 'Stain')
		self.assertEqual(ipa2asjp('ɛɐ̯də'), 'Ead3')
		self.assertEqual(ipa2asjp('fɔʏ̯ɐ'), 'foia')

		self.assertEqual(ipa2asjp('sʌn'), 'son')
		self.assertEqual(ipa2asjp('stɑː'), 'sto')
		self.assertEqual(ipa2asjp('ˈwɔːtə'), 'wot3')
		self.assertEqual(ipa2asjp('stəʊn'), 'st3un')
		self.assertEqual(ipa2asjp('ɜːθ'), '38')
		self.assertEqual(ipa2asjp('ˈfaɪə'), 'fai3')

	def test_asjp2ipa(self):
		"""
		ASJP strings should be converted into IPA-compliant strings.
		"""
		self.assertEqual(asjp2ipa(''), '')

		self.assertEqual(asjp2ipa('sloncE'), 'slont͡sɛ')
		self.assertEqual(asjp2ipa('zEmy~a'), 'zɛmʲa')

	def test_tokenise(self):
		"""
		ASJP strings should be correctly tokenised and non-compliant strings
		should raise ValueError.
		"""
		self.assertEqual(tokenise(''), [])
		self.assertEqual(tokenise('novE zEmy~E'), ['n', 'o', 'v', 'E', 'z', 'E', 'my~', 'E'])
		self.assertEqual(tokenise('a*kw~ndy$k"'), ['a*', 'kw~', 'ndy$', 'k"'])

		with self.assertRaises(ValueError): tokenise('*a')
		with self.assertRaises(ValueError): tokenise('"p')
		with self.assertRaises(ValueError): tokenise('a~')
		with self.assertRaises(ValueError): tokenise('aa$')
		with self.assertRaises(ValueError): tokenise('a~$')
