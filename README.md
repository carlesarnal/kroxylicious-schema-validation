# Validate Before Kafka: What Happens When a Proxy Enforces Your Schemas

The local test uses Kroxylicious 0.24.0, Apicurio Registry 3.3.3 and Kafka 3.9.1. A valid JSON order reaches the broker. A negative amount is rejected, as is the valid record sharing its batch. The script then reads the topic: success is a broker observation, not merely an absence of console errors.

## Current talk entry point

```sh
python3 talk/demo.py
```

Fresh integration check passed: valid, invalid, mixed batch, bypass, registry outage and recovery; broker contents asserted. The ephemeral Registry schema was restored after restart before retrying. No performance benchmark.

Start with [PRESENTATION_GUIDE.md](PRESENTATION_GUIDE.md), open `presentation.html`, and inspect [EVIDENCE.md](EVIDENCE.md) and [VERIFICATION.md](VERIFICATION.md). The obsolete custom-filter scaffold was removed; this implementation uses the released proxy.

The executable material and documentation distinguish observed behavior from design guidance. License: Apache-2.0.
