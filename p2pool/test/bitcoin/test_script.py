import unittest

from p2pool.bitcoin import script

class Test(unittest.TestCase):
    def test_all(self):
        data = bytes.fromhex('76  A9  14 89 AB CD EF AB BA AB BA AB BA AB BA AB BA AB BA AB BA AB BA  88 AC')
        self.assertEqual(
            list(script.parse(data)),
            [('UNK_118', None), ('UNK_169', None), ('PUSH', b'\x89\xab\xcd\xef\xab\xba\xab\xba\xab\xba\xab\xba\xab\xba\xab\xba\xab\xba\xab\xba'), ('UNK_136', None), ('CHECKSIG', None)],
        )
        self.assertEqual(script.get_sigop_count(data), 1)
