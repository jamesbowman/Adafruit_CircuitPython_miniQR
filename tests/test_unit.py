# SPDX-FileCopyrightText: 2024 James Bowman
#
# SPDX-License-Identifier: MIT

import unittest
import pytest

import adafruit_miniqr


REGILD = 0


def enc(msg, **args):
    _q = adafruit_miniqr.QRCode(**args)
    _q.add_data(msg)
    _q.make()
    return _q.matrix


class TestMiniQR(unittest.TestCase):
    def test_example(self):
        # Confirm the simple test that is in the docs
        msg = b"https://www.adafruit.com"
        _qr = adafruit_miniqr.QRCode()
        _qr.add_data(msg)
        _qr.make()
        with open("tests/test_example.gild") as _f:
            self.assertEqual(_f.read(), repr(_qr.matrix))

    def test_qr_type(self):
        # Confirm that qr_type 1-9 increases the matrix size
        expected_size = [None, 21, 25, 29, 33, 37, 41, 45, 49, 53]
        for _t in range(1, 10):
            _m = enc(b"abc", qr_type=_t)
            self.assertEqual(_m.width, _m.height)
            self.assertEqual(_m.width, expected_size[_t])

    def test_qr_error_correct(self):
        # Confirm that error correct L,M,Q,H give different matrix
        matrices = set()
        for _ec in (
            adafruit_miniqr.L,
            adafruit_miniqr.M,
            adafruit_miniqr.Q,
            adafruit_miniqr.H,
        ):
            _m = enc(b"abc", error_correct=_ec)
            matrices.add(_m)
        self.assertEqual(len(matrices), 4)  # All 4 are unique

    def test_qr_pattern_mask(self):
        # Confirm that pattern_mask 0-7 gives different matrix
        matrices = set()
        _qr = adafruit_miniqr.QRCode()
        _qr.add_data("test_qr_pattern_mask/1Z")
        for _m in range(8):
            _qr.make(mask_pattern=_m)
            matrices.add(tuple(_qr.matrix.buffer.buffer))
        self.assertEqual(len(matrices), 8)  # All 8 are unique

    def test_qr_auto(self):
        # Confirm that increasing message size increases the matrix size monotonically
        sizes = []
        for i in range(29):
            msg = b"aBc!1234" * i
            _m = enc(msg)
            sizes.append(_m.width)
        self.assertTrue(len(set(sizes)) > 1)
        self.assertEqual(sizes, sorted(sizes))

    def test_qr_str(self):
        # Confirm that bytes and str give the same result
        for _s in ("", "abc", "https://www.adafruit.com", "AbCd12"):
            _a = enc(_s.encode())
            _b = enc(_s)
            self.assertEqual(_a.buffer.buffer, _b.buffer.buffer)

    # See https://www.thonky.com/qr-code-tutorial/character-capacities
    capacities = {
        (1, adafruit_miniqr.L): 17,
        (1, adafruit_miniqr.M): 14,
        (1, adafruit_miniqr.Q): 11,
        (1, adafruit_miniqr.H): 7,
        (2, adafruit_miniqr.L): 32,
        (2, adafruit_miniqr.M): 26,
        (2, adafruit_miniqr.Q): 20,
        (2, adafruit_miniqr.H): 14,
        (3, adafruit_miniqr.L): 53,
        (3, adafruit_miniqr.M): 42,
        (3, adafruit_miniqr.Q): 32,
        (3, adafruit_miniqr.H): 24,
        (4, adafruit_miniqr.L): 78,
        (4, adafruit_miniqr.M): 62,
        (4, adafruit_miniqr.Q): 46,
        (4, adafruit_miniqr.H): 34,
        (5, adafruit_miniqr.L): 106,
        (5, adafruit_miniqr.M): 84,
        (5, adafruit_miniqr.Q): 60,
        (5, adafruit_miniqr.H): 44,
        (6, adafruit_miniqr.L): 134,
        (6, adafruit_miniqr.M): 106,
        (6, adafruit_miniqr.Q): 74,
        (6, adafruit_miniqr.H): 58,
        (7, adafruit_miniqr.L): 154,
        (7, adafruit_miniqr.M): 122,
        (7, adafruit_miniqr.Q): 86,
        (7, adafruit_miniqr.H): 64,
        (8, adafruit_miniqr.L): 192,
        (8, adafruit_miniqr.M): 152,
        (8, adafruit_miniqr.Q): 108,
        (8, adafruit_miniqr.H): 84,
        (9, adafruit_miniqr.L): 230,
        (9, adafruit_miniqr.M): 180,
        (9, adafruit_miniqr.Q): 130,
        (9, adafruit_miniqr.H): 98,
    }

    longstring = "IiLBXI9F2RHMQx9Z2N6XxTwd1dsUNGtjsajTsobRrBBDSq00oHXvrH0GyDFWx3zzpNKqv2iSF42n6FAw3VbiQq3AEK3O1kxQnPzsg8cltM9ch7cpRjIp0UP3r0AWCZ4K28YrvCV4oFZmhFbvyVxi37pQyff0qy9tUMUE4Et4UHD8AR56TTMJM4LchSuhejae7J2l9UrOua26i0rruUjm0uk4rVEPspoa0HATkfx"  # pylint: disable=line-too-long

    def test_capacities(self):
        for (_ty, _ec), n in self.capacities.items():
            # Should succeed for n, RuntimeError for n+1
            _qr = adafruit_miniqr.QRCode(qr_type=_ty, error_correct=_ec)
            _qr.add_data(self.longstring[:n])
            _qr.make()

            _qr = adafruit_miniqr.QRCode(qr_type=_ty, error_correct=_ec)
            _qr.add_data(self.longstring[: n + 1])
            with pytest.raises(RuntimeError):
                _qr.make()

    def test_qr_all(self):
        for _ty in range(1, 10):
            for _ec in (
                adafruit_miniqr.M,
                adafruit_miniqr.L,
                adafruit_miniqr.H,
                adafruit_miniqr.Q,
            ):
                _qr = adafruit_miniqr.QRCode(qr_type=_ty, error_correct=_ec)
                _qr.add_data(self.longstring[: self.capacities[(_ty, _ec)]])
                for _m in range(8):
                    _qr.matrix = None
                    _qr.make(mask_pattern=_m)
                    self.assertTrue(_qr.matrix is not None)
                    gildfile = f"tests/test_qr_all_{_ty}{_ec}{_m}.gild"
                    if REGILD:
                        with open(gildfile, "w") as _f:
                            _f.write(repr(_qr.matrix))
                    else:
                        with open(gildfile) as _f:
                            self.assertEqual(_f.read(), repr(_qr.matrix))

    def test_qr_maximum(self):
        msg = self.longstring[:230]
        _a = enc(msg)
        self.assertTrue(_a is not None)


if __name__ == "__main__":
    unittest.main()
