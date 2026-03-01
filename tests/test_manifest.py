import pytest

from PW_DOMAIN.interfaces.manifest.MANIFEST import MANIFEST


def _manifest_dict():
    return {
        'Identity': {
            'Domain': 'example.com',
            'Name': 'Example',
            'Translations': [
                {'Language': 'en-us', 'Translation': 'Example'},
                {'Language': 'pt-pt', 'Translation': 'Exemplo'},
            ]
        },
        'Trusts': [
            {
                'Action': 'GRANT',
                'Role': 'VAULT',
                'Queries': ['example.com/TEST/*'],
                'Domains': ['consumer.com']
            }
        ]
    }


def test_manifest_identity_and_translation():
    m = MANIFEST(_manifest_dict())
    assert m.RequireDomain() == 'example.com'
    assert m.GetName() == 'Example'
    assert m.Translate('pt-pt') == 'Exemplo'
    assert m.Translate('fr-fr') == 'Example'


def test_manifest_is_trustable():
    m = MANIFEST(_manifest_dict())
    assert m.IsTrustable(target='consumer.com', role='VAULT', code='example.com/TEST/1') is True
    assert m.IsTrustable(target='consumer.com', role='CONSUMER', code='example.com/TEST/1') is False


def test_manifest_verify_identity():
    m = MANIFEST(_manifest_dict())
    m.VerifyIdentity('example.com')
    with pytest.raises(Exception):
        m.VerifyIdentity('other.com')
