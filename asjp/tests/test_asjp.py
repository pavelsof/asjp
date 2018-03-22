from unittest import TestCase

from asjp import ipa2asjp



class ApiTestCase(TestCase):

	def test_ipa2asjp(self):
		"""
		IPA-compliant strings should be correctly converted to ASJP.

		The IPA strings are sourced from NorthEuraLex (bul, deu, eng), their
		ASJP counterparts are derived manually.
		"""
		self.assertEqual(ipa2asjp('sɫɤnt͡sɛ'), 'sloncE')
		self.assertEqual(ipa2asjp('zvɛzda'), 'zvEzdE')
		self.assertEqual(ipa2asjp('vɔda'), 'vodE')
		self.assertEqual(ipa2asjp('kamɤk'), 'kEmok')
		self.assertEqual(ipa2asjp('zɛmʲa'), 'zEmy~E')
		self.assertEqual(ipa2asjp('ɔɡɤn'), 'ogon')

		self.assertEqual(ipa2asjp('zɔnə'), 'zon3')
		self.assertEqual(ipa2asjp('ʃtɐn'), 'Stan')
		self.assertEqual(ipa2asjp('vasɐ'), 'vEsa')
		self.assertEqual(ipa2asjp('ʃtaɪ̯n'), 'StEin')
		self.assertEqual(ipa2asjp('ɛɐ̯də'), 'Ead3')
		self.assertEqual(ipa2asjp('fɔʏ̯ɐ'), 'foia')

		self.assertEqual(ipa2asjp('sʌn'), 'son')
		self.assertEqual(ipa2asjp('stɑː'), 'sto')
		self.assertEqual(ipa2asjp('ˈwɔːtə'), 'wot3')
		self.assertEqual(ipa2asjp('stəʊn'), 'st3un')
		self.assertEqual(ipa2asjp('ɜːθ'), '38')
		self.assertEqual(ipa2asjp('ˈfaɪə'), 'fEi3')
