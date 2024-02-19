# Kroxylicious WASM Filter Sample

This sample filter project provides an example usage of [custom filters](https://kroxylicious.io/kroxylicious/#_custom_filters) in Kroxylicious.
Here we leverage the Apicurio Registry schema validation libraries [Apicurio Registry](https://github.com/Apicurio/apicurio-registry-schema-validation) to validate the schema being used.

To learn more about Kroxylicious, visit the [docs](https://kroxylicious.io/kroxylicious).
To learn more about Apicurio Registry, visit the [docs](https://www.apicur.io/registry/docs/apicurio-registry/2.5.x/index.html).

## Getting started

### Build
Building the sample project is easy!
```shell
mvn verify
```
### Configure
Filters can be added and removed by altering the `filters` list in the `sample-proxy-config.yml` file. You can also reconfigure the sample filters by changing the configuration values in this file.
The **SampleFetchResponseFilter** and **SampleProduceRequestFilter** each have two configuration values that must be specified for them to work:

#### Default Configuration
The default configuration for **SampleProduceRequestFilter** is:
```yaml
filters:
  - type: SampleProduceRequestFilterFactory
    config:
```
The default configuration for **SampleFetchResponseFilter** is:
```yaml
filters:
  - type: SampleFetchResponseFilterFactory
    config:
```
