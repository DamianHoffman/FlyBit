import argparse
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "skills", "sms-check", "scripts"))
import sms_segments as s  # noqa: E402


def args():
    return argparse.Namespace(link_len=23, optout_len=30, token_len=8, recipients=None, price=None)


class Encoding(unittest.TestCase):
    def test_gsm_alphabet_has_127_characters(self):
        self.assertEqual(len(s.GSM7_BASIC), 127)

    def test_plain_text_is_gsm7(self):
        m = s.measure("Hello")
        self.assertTrue(m["gsm7"])
        self.assertEqual(m["segments"], 1)

    def test_polish_letters_force_unicode(self):
        self.assertFalse(s.measure("ę")["gsm7"])

    def test_smart_quotes_and_dash_force_unicode(self):
        self.assertFalse(s.measure("\u201etest\u201d")["gsm7"])
        self.assertFalse(s.measure("a \u2013 b")["gsm7"])


class Segments(unittest.TestCase):
    def test_gsm7_boundaries(self):
        seg = lambda n: s.measure("a" * n)["segments"]
        self.assertEqual((seg(160), seg(161), seg(306), seg(307)), (1, 2, 2, 3))

    def test_unicode_boundaries(self):
        seg = lambda n: s.measure("\u0105" * n)["segments"]
        self.assertEqual((seg(70), seg(71), seg(134), seg(135)), (1, 2, 2, 3))

    def test_extension_characters_count_double(self):
        self.assertEqual(s.measure("\u20ac" * 80)["segments"], 1)
        self.assertEqual(s.measure("\u20ac" * 81)["segments"], 2)

    def test_emoji_is_two_units_and_not_split(self):
        self.assertEqual(s.measure("\U0001F600" * 35)["segments"], 1)
        self.assertEqual(s.measure("\U0001F600" * 36)["units"], 72)
        t = "\u0105" + "a" * 65 + "\U0001F600" * 33 + "bb"
        self.assertEqual(s.measure(t)["units"], 134)
        self.assertEqual(s.measure(t)["segments"], 3)

    def test_empty_message(self):
        self.assertEqual(s.measure("")["segments"], 0)


class Conversion(unittest.TestCase):
    def test_cyrillic_cannot_be_converted_and_is_not_offered_as_gsm(self):
        a = args()
        r = s.analyze_message("\u041f\u0440\u0438\u0432\u0435\u0442", a)
        self.assertFalse(r["plain_variant"]["gsm7"])
        self.assertEqual(len(r["plain_variant"]["unconvertible"]), 6)
        a.recipients, a.price = 100, 1.0
        self.assertNotIn("plain", s.analyze_message("\u041f\u0440\u0438\u0432\u0435\u0442", a)["cost"])

    def test_offender_groups_are_language_neutral(self):
        o = s.offenders("Za\u017c\u00f3\u0142\u0107 \u201ex\u201d \U0001F600")
        self.assertEqual(set(o), {"letters", "typographic", "emoji"})
        self.assertEqual(set(s.offenders("\u041f\u0440\u0438\u0432\u0435\u0442")), {"letters"})

    def test_polish_and_typography_to_gsm(self):
        out, left = s.to_gsm("Za\u017c\u00f3\u0142\u0107 g\u0119\u015bl\u0105 ja\u017a\u0144 \u2013 \u201etest\u201d \u2026")
        self.assertEqual(out, 'Zazolc gesla jazn - "test" ...')
        self.assertEqual(left, [])
        self.assertTrue(s.measure(out)["gsm7"])

    def test_emoji_cannot_be_converted(self):
        out, left = s.to_gsm("Cze\u015b\u0107 \U0001F600")
        self.assertEqual(left, ["\U0001F600"])
        self.assertTrue(out.startswith("Czesc"))


class Placeholders(unittest.TestCase):
    def test_tokens_and_link_are_expanded(self):
        r = s.analyze_message("Dzien dobry {{ first_name }}, info: [LINK]", args())
        self.assertTrue(r["gsm7"])
        self.assertEqual(r["units"], len("Dzien dobry ") + 8 + len(", info: ") + 23)

    def test_polish_letter_next_to_token_is_unicode(self):
        self.assertFalse(s.analyze_message("Cze\u015b\u0107 {imie}, [LINK]", args())["gsm7"])

    def test_cost_compares_plain_variant(self):
        a = args()
        a.recipients, a.price = 1000, 0.1
        r = s.analyze_message("Cze\u015b\u0107 " + "a" * 100, a)
        self.assertEqual(r["segments"], 2)
        self.assertEqual(r["plain_variant"]["segments"], 1)
        self.assertEqual(r["cost"], {"current": 200.0, "plain": 100.0})


class Cli(unittest.TestCase):
    def test_multiple_messages_split_by_separator(self):
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write("Pierwsza \u0105\n---\nDruga\n")
            name = f.name
        try:
            a = argparse.Namespace(text=None, file=name)
            self.assertEqual(s.read_messages(a), ["Pierwsza \u0105", "Druga"])
        finally:
            os.unlink(name)


if __name__ == "__main__":
    unittest.main()
