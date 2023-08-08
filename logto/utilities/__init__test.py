from . import removeFalsyKeys, urlsafeEncode


class TestRemoveFalsyKeys:
    def test_shouldRemoveNoneAndEmptyString(self):
        assert removeFalsyKeys(
            {
                "a": None,
                "b": "",
                "c": "c",
            }
        ) == {
            "c": "c",
        }

    def test_shouldRemoveFalse(self):
        assert removeFalsyKeys(
            {
                "a": False,
                "b": True,
            }
        ) == {
            "b": True,
        }


class TestUrlsafeEncode:
    def test_shouldEncode(self):
        assert urlsafeEncode(b"123") == "MTIz"

    def test_shouldRemovePadding(self):
        assert urlsafeEncode(b"1234") == "MTIzNA"

    def test_shouldReplaceUnsafeCharacters(self):
        assert (
            urlsafeEncode(
                b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f"
            )
            == "AAECAwQFBgcICQoLDA0ODw"
        )

    def test_shouldReplaceUnsafeEncodedCharacters(self):
        assert urlsafeEncode(b"\xff\xff") == "__8"
