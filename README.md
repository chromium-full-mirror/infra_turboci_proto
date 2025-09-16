# TurboCI

TurboCI is an in-development private-access API for Google's own continuous
integration of Android, Chrome, ChromeOS, and other large software projects.

This repo contains the protobuf definitions for the service API and objects
used by the service for integration with Googler-owned Open Source CI related
infrastructure in Open Source software such as Chromium.

# Working with the repo

## Getting the repo

This repo uses [depot_tools] for obtaining the pinned copy of `protoc` and `buf`
via the DEPS file. You can install it with [these instructions].

Checking out this repo can be done by directly cloning this repo and then
inside it running:

```
$ gclient sync
```

Which will pull the pinned `protoc` and `buf` binaries into ./tools.

[these instructions]: https://commondatastorage.googleapis.com/chrome-infra-docs/flat/depot_tools/docs/html/depot_tools_tutorial.html#_setting_up

## Making Changes

This repo uses `buf breaking` to check that your CL doesn't introduce [backwards
incompatible changes]. This is verified by the Commit Queue for this project
which will be activated when CLs in this repo are uploaded to Gerrit and marked
for submission.

You can run all checks and build `turboci.desc` by running:

```
$ ./build.py
```

This will run the pinned `buf lint` and `buf breaking` commands, as well as
re-build `turboci.desc`.

## Skipping breaking build checks

You don't usually want to do this, but it can be OK as long as you know that the
affected fields are not being used by anything in production. Please see
[backwards incompatible changes] for guidance.

To skip breaking change checks, upload your CL and then add the following footer
to the CL description in Gerrit:

```
Breaking-Proto-Change-Ok: Some reason.
```

Other checks cannot be skipped.

# Repo layout

This repo primarially consists of the `turboci` subfolder with the following
proto packages:

  * turboci.data.v1 - Common data messages used as the Anys in Check Options, Check
    Results or Stage Arguments, or common atoms embedded in such messages. You're
    probably here because you need to interact with something in the data namespace.
    See [#Data Annotations].

  * turboci.orchestrator.v1 - The TurboCIOrchestrator Service. Everything
    interacting with the TurboCI Orchestrator will deal with the messages
    here, including Checks, Stages and their related messages, but not the
    contents of the Any fields in this API (e.g. CheckOptions, Check.Result Data
    Stage Args, Edit Reasons, etc.).

  * turboci.executor.v1 - This is the RPC interface implemented by TurboCI
    Executors (external services which the TurboCI Orchestrator connects to in
    order to actually execute Stages). Very few things need to worry about this
    API.

# Data Annotations

Messages in the `turboci.data.v1` namespaces have the following annotations:

  * TBD: Option for maturity
  * TBD: Option for audience
  * TBD: Option for intended usage (check option (per kind), check result (per
    kind), stage args, embedded)


[depot_tools]: https://chromium.googlesource.com/chromium/tools/depot_tools.git
[backwards incompatible changes]: https://protobuf.dev/programming-guides/editions/#updating
