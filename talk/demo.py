"""Assert producer errors AND broker contents against the released proxy."""
import json
from pathlib import Path
import subprocess
import time
import urllib.request

ROOT = Path(__file__).resolve().parent


def compose(*args, data=None, check=True):
    result = subprocess.run(['docker', 'compose', '-p', 'proxy-talk', '-f', str(ROOT / 'compose.yaml'),
                             *args], input=data, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, timeout=180)
    if check and result.returncode:
        raise RuntimeError(result.stdout)
    return result.stdout


def produce(records, endpoint='kroxylicious:9192'):
    return compose('exec', '-T', 'kafka', '/opt/kafka/bin/kafka-console-producer.sh',
                   '--bootstrap-server', endpoint, '--topic', 'orders',
                   '--producer-property', 'acks=all', '--producer-property', 'retries=0',
                   '--producer-property', 'linger.ms=2000', '--producer-property', 'batch.size=65536',
                   '--producer-property', 'delivery.timeout.ms=10000',
                   '--producer-property', 'request.timeout.ms=5000',
                   data='\n'.join(json.dumps(r) for r in records) + '\n', check=False)


def record(identity, amount=10):
    return {'orderId': identity, 'amount': amount}


def read_records():
    output = compose('exec', '-T', 'kafka', '/opt/kafka/bin/kafka-console-consumer.sh',
                     '--bootstrap-server', 'kafka:9092', '--topic', 'orders',
                     '--from-beginning', '--timeout-ms', '5000', check=False)
    return [json.loads(line) for line in output.splitlines() if line.startswith('{')]


def run():
    target = ROOT / 'target'
    target.mkdir(exist_ok=True)
    try:
        compose('up', '-d', '--wait', 'kafka', 'registry')
        schema = {'type': 'object', 'required': ['orderId', 'amount'], 'properties': {
            'orderId': {'type': 'string'}, 'amount': {'type': 'number', 'minimum': 0}}}
        body = {'artifactId': 'orders', 'artifactType': 'JSON', 'firstVersion': {
            'content': {'content': json.dumps(schema), 'contentType': 'application/json'}}}
        for attempt in range(60):
            try:
                req = urllib.request.Request('http://localhost:18182/apis/registry/v3/groups/default/artifacts',
                                             data=json.dumps(body).encode(), headers={'Content-Type': 'application/json'})
                with urllib.request.urlopen(req, timeout=10) as response:
                    content_id = json.load(response)['version']['contentId']
                break
            except OSError:
                if attempt == 59:
                    raise
                time.sleep(2)
        template = (ROOT / 'proxy.yaml.template').read_text()
        (target / 'proxy.yaml').write_text(template.replace('__ID__', str(content_id)))
        compose('--profile', 'proxy', 'up', '-d', 'kroxylicious')
        compose('exec', '-T', 'kafka', '/opt/kafka/bin/kafka-topics.sh', '--bootstrap-server',
                'kafka:9092', '--create', '--topic', 'orders', '--partitions', '1', '--replication-factor', '1')
        time.sleep(8)
        logs = {}
        logs['valid'] = produce([record('valid')])
        assert 'InvalidRecordException' not in logs['valid'], logs['valid']
        assert [r['orderId'] for r in read_records()] == ['valid']
        logs['invalid'] = produce([record('invalid', -1)])
        assert 'InvalidRecordException' in logs['invalid'], logs['invalid']
        logs['mixed'] = produce([record('mixed-valid'), record('mixed-invalid', -1)])
        assert 'InvalidRecordException' in logs['mixed'], logs['mixed']
        assert [r['orderId'] for r in read_records()] == ['valid'], 'rejected records reached broker'
        logs['bypass'] = produce([record('bypass', -1)], 'kafka:9092')
        assert {r['orderId'] for r in read_records()} == {'valid', 'bypass'}
        compose('stop', 'registry')
        logs['outage'] = produce([record('outage')])
        assert 'SCHEMA_RESOLUTION_ERROR' in logs['outage'], logs['outage']
        assert {r['orderId'] for r in read_records()} == {'valid', 'bypass'}
        compose('start', 'registry')
        for attempt in range(60):
            try:
                with urllib.request.urlopen('http://localhost:18182/apis/registry/v3/system/info', timeout=5):
                    break
            except OSError:
                if attempt == 59:
                    raise
                time.sleep(2)
        # This laboratory Registry uses ephemeral storage. Restore its schema
        # after restart and verify the configured content ID before retrying.
        with urllib.request.urlopen(req, timeout=10) as response:
            restored_id = json.load(response)['version']['contentId']
        assert restored_id == content_id, 'proxy must be reconfigured if content identity changes'
        logs['recovery'] = produce([record('recovered')])
        (target / 'producer-results.json').write_text(json.dumps(logs, indent=2))
        assert {r['orderId'] for r in read_records()} == {'valid', 'bypass', 'recovered'}, logs['recovery']
        print('PASS: valid, invalid, mixed batch, bypass, outage and recovery broker assertions')
    finally:
        compose('--profile', 'proxy', 'down', '-v', check=False)


if __name__ == '__main__':
    run()
