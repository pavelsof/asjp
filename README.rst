====
asjp
====

A small library of three functions. ``ipa2asjp`` takes an IPA-encoded sequence
and converts it into an ASJP-encoded sequence. ``asjp2ipa`` tries to do the
opposite. ``tokenise`` takes an ASJP-encoded string and returns a list of
tokens.

>>> from asjp import ipa2asjp, asjp2ipa, tokenise
>>> ipa2asjp('zɛmʲa')
'zEmy~E'
>>> tokenise(ipa2asjp('zɛmʲa'))
['z', 'E', 'my~', 'E']
>>> ipa2asjp(['z', 'ɛ', 'mʲ', 'a']) == tokenise(ipa2asjp('zɛmʲa'))
True
>>> asjp2ipa('zEmy~E')
'zamʲa'

ASJPcode, now commonly known as ASJP, is a simplified transcription alphabet
introduced and specified by `Brown et al. (2009)`_. It is used for transcribing
the `ASJP Database`_ and in computational historical linguistics in general.


licence
=======

MIT. Do as you please and praise the snake gods.


.. _`Brown et al. (2009)`: https://doi.org/10.1524/stuf.2008.0026
.. _`ASJP Database`: http://asjp.clld.org/
