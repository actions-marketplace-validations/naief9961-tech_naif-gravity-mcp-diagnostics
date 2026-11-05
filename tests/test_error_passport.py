"""Error Passport regression: all network tests use ephemeral loopback fixtures."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / 'tools'
sys.path.insert(0, str(TOOLS))
import error_passport as passport
from test_mcp_health_check import fixture

SCRIPT = str(TOOLS / 'error_passport.py')
SECRET = 'fixture-top-secret-should-never-leak'


def example(status='pass'):
    report = {
        'schema_version': '1.0',
        'status': status,
        'exit_code': 0 if status == 'pass' else 1,
        'requested_protocol_version': '2025-06-18',
        'negotiated_protocol_version': '2025-11-25' if status == 'pass' else None,
        'session_present': True if status == 'pass' else False,
        'tools_advertised': True if status == 'pass' else None,
        'tool_count': 2 if status == 'pass' else None,
        'tools_executed': False,
        'requests': [
            {'method': 'initialize', 'http_status': 200}
        ],
        'error': None if status == 'pass' else {
            'code': 'discovery_failed',
            'method': 'initialize',
            'message': 'mismatched request ID or invalid response shape',
        },
    }
    return report


class PassportTests(unittest.TestCase):
    def test_healthy_does_not_upsell_even_if_requested(self):
        report = example()
        p = passport.make_passport(report, include_optional_service=True)
        self.assertEqual(p['result'], 'BOUNDED_DISCOVERY_PASS')
        self.assertEqual(p['category'], 'healthy')
        self.assertNotIn('optional_service', p)
        self.assertIsNone(p['free_guide'])
        self.assertFalse(p['automatic_payment'])
        self.assertFalse(p['automatic_repair'])
        self.assertNotIn('naifgravity.com/service/', passport.markdown(p))

    def test_failure_is_diagnosis_not_repair(self):
        p = passport.make_passport(example('fail'), include_optional_service=True)
        self.assertEqual(p['result'], 'DIAGNOSIS_ONLY')
        self.assertEqual(p['category'], 'rpc_contract')
        self.assertIn('optional_service', p)
        self.assertEqual(p['evidence']['failed_at'], 'initialize')
        self.assertIn('No tools/call', ' '.join(p['limitations']))
        self.assertNotIn('repaired', json.dumps(p).lower())

    def test_unknown_metadata_and_error_message_never_leak(self):
        report = example('fail')
        report['metadata'] = {'raw_endpoint': 'https://site.example/?key=' + SECRET}
        report['error']['message'] = 'Authorization: Bearer ' + SECRET
        p = passport.make_passport(report, include_optional_service=True)
        self.assertEqual(p['category'], 'unknown')
        rendered = json.dumps(p) + passport.markdown(p)
        self.assertNotIn(SECRET, rendered)
        self.assertNotIn('site.example', rendered)
        self.assertNotIn('Bearer', rendered)

    def test_evidence_fingerprint_ignores_untrusted_fields(self):
        a = example('fail')
        b = copy.deepcopy(a)
        b['private_uri'] = 'https://example.test/?secret=' + SECRET
        b['error']['extra_header'] = SECRET
        p1 = passport.make_passport(a)
        p2 = passport.make_passport(b)
        self.assertEqual(p1['fingerprint'], p2['fingerprint'])

    def test_auth_error_has_no_paid_referral(self):
        r = example('fail')
        r['error']['message'] = 'HTTP 401 (response body omitted)'
        p = passport.make_passport(r, include_optional_service=True)
        self.assertEqual(p['category'], 'authentication')
        self.assertNotIn('optional_service', p)

    def test_nonreport_and_execution_are_rejected(self):
        for key, value in [('schema_version', '2.0'),
                           ('tools_executed', True),
                           ('status', 'fixed')]:
            with self.subTest(key=key):
                r = example()
                r[key] = value
                with self.assertRaises(ValueError):
                    passport.make_passport(r)

    def test_input_size_is_bounded(self):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / 'big.json'
            file.write_text('a' * (passport.MAX_INPUT + 1))
            proc = subprocess.run([sys.executable, SCRIPT, '--report', str(file)],
                                  text=True, capture_output=True)
            self.assertEqual(proc.returncode, 2)
            self.assertNotIn('a' * 100, proc.stderr)

    def test_offline_cli_makes_no_network_calls(self):
        raw = json.dumps(example('fail'))
        proc = subprocess.run([sys.executable, SCRIPT, '--report', '-', '--format', 'json'],
                              input=raw, text=True, capture_output=True)
        self.assertEqual(proc.returncode, 1)
        output = json.loads(proc.stdout)
        self.assertEqual(output['mode'], 'offline')
        self.assertEqual(output['category'], 'rpc_contract')

    def test_network_requires_explicit_authorization(self):
        proc = subprocess.run(
            [sys.executable, SCRIPT, '--probe', 'https://example.com/mcp'],
            text=True, capture_output=True)
        self.assertEqual(proc.returncode, 2)
        self.assertIn('requires --authorized', proc.stderr)

    def test_reject_credentials_in_url_and_unencrypted_remote(self):
        for url in ('https://user:password@example.com/mcp',
                    'https://example.com/mcp?token=secret',
                    'http://example.com/mcp'):
            with self.subTest(url='redacted'):
                proc = subprocess.run(
                    [sys.executable, SCRIPT, '--probe', url, '--authorized'],
                    text=True, capture_output=True)
                self.assertEqual(proc.returncode, 2)
                self.assertNotIn('password', proc.stdout + proc.stderr)
                self.assertNotIn('token=secret', proc.stdout + proc.stderr)

    def test_loopback_probe_healthy_and_wrong_id(self):
        for mode, expected_status, expected_code in (
                ('json', 0, 'healthy'), ('wrong-id', 1, 'rpc_contract'),
                ('bad-schema', 1, 'tool_contract')):
            with self.subTest(mode=mode):
                with fixture(mode) as (url, requests):
                    proc = subprocess.run(
                        [sys.executable, SCRIPT, '--probe', url, '--authorized',
                         '--timeout', '3', '--format', 'json'],
                        text=True, capture_output=True, timeout=12)
                    self.assertEqual(proc.returncode, expected_status, proc.stderr)
                    p = json.loads(proc.stdout)
                    self.assertEqual(p['category'], expected_code)
                    self.assertEqual(p['mode'], 'authorized-local-probe')
                    self.assertFalse(p['automatic_payment'])
                    self.assertNotIn(url, proc.stdout)
                    self.assertTrue(requests)
                    self.assertNotIn('tools/call', [x[0]['method'] for x in requests])


if __name__ == '__main__':
    unittest.main()
