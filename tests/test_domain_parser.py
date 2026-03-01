import os

from PW_DOMAIN.parts.domain.DOMAIN_PARSER import DOMAIN_PARSER


def _write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as handle:
        handle.write(content)


def test_parse_domain(tmp_path):
    domain = 'example.com'
    folder = tmp_path / domain
    os.makedirs(folder, exist_ok=True)

    # Config
    _write(folder / f'🗺️ {domain}.yaml', f"""Domain: {domain}
Broker: broker.com
Roles: [VAULT]
""")

    # Manifest
    _write(folder / f'📜 {domain}.yaml', f"""Identity:
  Domain: {domain}
  Name: Example
Trusts:
  - Action: GRANT
    Role: VAULT
    Queries: ["{domain}/TEST/*"]
    Domains: ["consumer.com"]
""")

    cfg = DOMAIN_PARSER.ParseDomain(domain=domain, folder=str(folder))

    assert cfg.RequireDomain() == domain
    assert cfg.RequireConfig().RequireStr('Broker') == 'broker.com'
    manifest = cfg.RequireManifest(domain)
    assert manifest.RequireDomain() == domain
