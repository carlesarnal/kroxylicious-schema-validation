# Presentation guide

Validate Before Kafka: What Happens When a Proxy Enforces Your Schemas

## Audience and central claim

The local test uses Kroxylicious 0.24.0, Apicurio Registry 3.3.3 and Kafka 3.9.1. A valid JSON order reaches the broker. A negative amount is rejected, as is the valid record sharing its batch. The script then reads the topic: success is a broker observation, not merely an absence of console errors.

## 30-minute run of show

### 0:00 — Follow the order into Kafka

The local test uses Kroxylicious 0.24.0, Apicurio Registry 3.3.3 and Kafka 3.9.1. A valid JSON order reaches the broker. A negative amount is rejected, as is the valid record sharing its batch. The script then reads the topic: success is a broker observation, not merely an absence of console errors.

Run talk/demo.py and compare validation errors with records read directly from the broker.

### 4:00 — Registry failure is not malformed input

Stopping Registry causes a valid record to be rejected with SCHEMA_RESOLUTION_ERROR inside InvalidRecordException. Treating that exception as proof of bad input would send a valid business event down the wrong recovery path. Inspect the constraint or resolution context and the dependency before deciding whether to repair, quarantine or retry.

Locate SCHEMA_RESOLUTION_ERROR in the producer output after Registry stops.

### 9:00 — Restore the schema before retrying

Our demonstration Registry uses ephemeral storage. Restarting its container restored HTTP availability but not the registered schema. The first recovery assertion failed with ContentNotFoundException. The corrected lab re-registers the schema and verifies its content ID before retrying. This is a laboratory restoration step, not a substitute for production Registry persistence and backup.

Show schema restoration and the content-ID check before sending the recovery record.

### 15:00 — Batch semantics and bypass routes

An invalid event sent directly to the broker bypasses the filter. Deployment controls must enforce the proxy path. Likewise, a rejected mixed batch does not give an application a universal selective-resend algorithm: preserve its ordering and duplicate-handling requirements. My merged Avro/Protobuf contribution explains the implementation background; this particular lab exercises JSON Schema.

Compare the bypassed invalid record with the rejected mixed batch.

### 21:00 — Choose the appropriate recovery action

Summarize the decision the example supports and the assumptions behind it.

Use failure-matrix.txt to choose input repair, dependency recovery or routing correction.

### 26:00 — Questions and buffer

Ask what the demonstration establishes and what it leaves open. Do not add another feature if time is short.

## Setup and fallback

```sh
python3 talk/demo.py
```

Fresh integration check passed: valid, invalid, mixed batch, bypass, registry outage and recovery; broker contents asserted. The ephemeral Registry schema was restored after restart before retrying. No performance benchmark.

Prebuild/download dependencies. Keep a recording of an actual successful run; if unavailable, use the documented walkthrough and say it is not live execution. Never substitute fabricated success output.

## Questions to prepare

- What is the simplest alternative?
- Which failure was actually exercised?
- Which guarantee belongs to the application rather than the infrastructure?
- Which result changes with versions or workload?

## 25-minute adaptation

Use one central trace, shorten setup and reserve three minutes for questions. Move the secondary implementation example to backup.
