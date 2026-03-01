import pytest

from PW_DOMAIN.interfaces.msg.MSG import MSG


class DummyValidator:
    def __init__(self, expected_hash: str, verified: bool = True):
        self._expected_hash = expected_hash
        self._verified = verified

    def ValidateSignature(self, text: str, hash: str, publicKey: str, signature: str):
        return {
            'hash': self._expected_hash,
            'isVerified': self._verified,
        }


def _build_msg():
    msg = MSG.Wrap(to='receiver.com', subject='AnyMethod', body={'A': 1})
    msg.RequireFrom('sender.com')
    msg.RequireHash('abc')
    msg.RequireSignature('sig')
    return msg


def test_wrap_and_verify_header():
    msg = MSG.Wrap(to='receiver.com', subject='AnyMethod')
    msg.RequireFrom('sender.com')
    msg.VerifyHeader()


def test_match_subject_requires_expected_to():
    msg = MSG.Wrap(to='receiver.com', subject='AnyMethod')
    msg.RequireFrom('sender.com')
    with pytest.raises(ValueError):
        msg.MatchSubject('AnyMethod')


def test_match_subject_ok():
    msg = MSG.Wrap(to='receiver.com', subject='AnyMethod')
    msg.RequireFrom('sender.com')
    msg.MatchSubject('AnyMethod', expectedTo='receiver.com')


def test_verify_signature_requires_validator():
    msg = _build_msg()
    with pytest.raises(ValueError):
        msg.VerifySignature(publicKey='pk', validator=None)


def test_verify_signature_uses_validator():
    msg = _build_msg()
    validator = DummyValidator(expected_hash='abc', verified=True)
    msg.VerifySignature(publicKey='pk', validator=validator)


def test_verify_signature_hash_mismatch():
    msg = _build_msg()
    validator = DummyValidator(expected_hash='zzz', verified=True)
    with pytest.raises(Exception):
        msg.VerifySignature(publicKey='pk', validator=validator)
