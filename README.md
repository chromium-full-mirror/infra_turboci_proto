# TurboCI

TurboCI is an in-development private-access API for Google's own continuous
integration of Android, Chrome, ChromeOS, and other large software projects.

This repo contains the protobuf definitions for the service API and objects used
by the service for integration with Googler-owned Open Source CI related
infrastructure in Open Source software such as Chromium.

## Working with the repo

### Getting the repo

This repo uses [depot_tools] for obtaining the pinned copy of `protoc` and `buf`
via the DEPS file. You can install it with [these instructions].

Checking out this repo can be done by directly cloning this repo and then inside
it running:

```
$ gclient sync
```

Which will pull the pinned `protoc` and `buf` binaries into ./tools.

[these instructions]: https://commondatastorage.googleapis.com/chrome-infra-docs/flat/depot_tools/docs/html/depot_tools_tutorial.html#_setting_up

### Making Changes

This repo uses `buf breaking` to check that your CL doesn't introduce
[backwards incompatible changes]. This is verified by the Commit Queue for this
project which will be activated when CLs in this repo are uploaded to Gerrit and
marked for submission.

You can format the protos, run all checks and build the go stubs by running:

```
$ ./build.py all
```

### Skipping breaking build checks

You don't usually want to do this, but it can be OK as long as you know that the
affected fields are not being used by anything in production. Please see
[backwards incompatible changes] for guidance.

To skip breaking change checks, upload your CL and then add the following footer
to the CL description in Gerrit:

```
Breaking-Proto-Change-Ok: Some reason.
```

Other checks cannot be skipped.

## Repo layout

This repo primarially consists of the `turboci` subfolder with the following
proto packages:

*   `turboci.data.<feature>.v1` - Data messages to be used as the Anys in Check
    Options and Check Results to support some logical feature. Features should
    be selected to form logical groups where someone using any message in the
    namespace is likely to want to use ALL messages in that namespace. It's
    allowed to use additional hierarchy here to group many related stages
    together.

*   `turboci.stages.<function>.v1` - Stage args for some logical function. It's
    allowed to use additional hierarchy here to group many related stages
    together.

*   `turboci.graph.ids.v1` - Identifiers for objects in a TurboCI Graph. This is
    separate from `turboci.graph.orchestrator.v1` to allow these IDs to be
    included in other messages without pulling in all the rest of the protos.

*   `turboci.graph.orchestrator.v1` - The TurboCI Orchestrator Service.
    Everything interacting with the TurboCI Orchestrator will deal with the
    messages here, including Checks, Stages and their related messages, but not
    the contents of the Any fields in this API (e.g. Check Options, Check
    Results, Stage Args, Edit Reasons, etc.).

*   `turboci.graph.executor.v1` - This is the RPC interface implemented by
    TurboCI Executors (external services which the TurboCI Orchestrator connects
    to in order to actually execute Stages). Very few things need to worry about
    this API.

Additionally, go stubs are generated in the `go` folder. The `google` folder
contains just an unmodified copy of `google/api/field_behavior.proto` for
standalone compilation/linting.

### GoPackage option

Every ...v1 package must have a `go_package` option as follows:

Given `package turboci.a.b.c.v1`, a given proto file would have a `go_package`
value of:

```
go.chromium.org/turboci/proto/go/a/b/c/v1;cpb
```

Unless this proto file contains a `service` definition, in which case it would
have a `go_package` value of:

```
go.chromium.org/turboci/proto/go/a/b/c/v1/grpcpb;cgrpcpb
```

Additionally:

*   proto files with service definitions must not have any other top-level
    definitions.
*   packages are limited to a maximum of one service definition.

### Why this repo layout?

There are a couple competing requirements we are trying to achieve:

*   Programs should always be able to only link the protos they need.
*   Programs should be able to manipulate all data types without having to link
    in the RPC stubs.
*   We want to be able to introduce some features as experiments, or possibly
    product-specific features, and later elevate them to be generally-available
    features, without having to do a migration (e.g. to rename them or move them
    to a new package).

There are also some requirements we considered adhering to, but are explicitly
avoiding:

#### (Google Internal) Every .proto file is its own build target

This is considered best practice inside of Google, but is incompatible with the
way that Go (and other languages) actually interact with protos outside of
Google. If we followed this adage to the letter, it would mean that using N
messages from this repo would require N different Go package imports, and we
would also have to fight protoc-gen-go to make every .proto file in its own Go
package (my experiments show that even when you get all the imports and
`go_package` options right, the generated code will still result in a cycle due
to 'underscore' imports of parent packages).

Our compromise here is to make it so that each logical group of definitions is
inside the same proto package, but those packages are always treated as an
atomic unit both inside and outside of Google.

#### (Google Internal) Every .proto has exactly one top-level definition

(and also avoid nested definitions at all costs)

This is meant to be used in conjunction with the previous 'every .proto file is
its own build target' requirement. The theory here is that it helps alleviate
the build dependency graph when importing some small proto. If every definition
is a separate proto file, then you can target exactly what you need. If you have
larger protos, then you run the risk of "including a small message" resulting in
a dependency on a massive collection of protos.

Our compromise here is to break things up by feature (and also make a special
case for graph IDs which tend to show up in many lightweight contexts which
don't need any of the graph node definitions). This still gives some granular
control over which options/results/stages a given program needs to worry about,
without decomposing all the way down to the single-definition level.

#### aip.dev/191

Confusingly, aip.dev/191 recommends putting service and request/response
messages in the same file. We specifically don't want to do this to allow the
maximum amount of message manipulation without requiring linking to the rpc
apparatus.

Our compromise here requires just the service definition on its own, and the
request/response messages in with the other regular protos.

## Data Annotations (TBD)

Messages in the `turboci.{data,stages}.v1` namespaces have the following
annotations:

*   TBD: Option for maturity
*   TBD: Option for audience
*   TBD: Option for intended usage (check option (per kind), check result (per
    kind), stage args, embedded)

[depot_tools]: https://chromium.googlesource.com/chromium/tools/depot_tools.git
[backwards incompatible changes]: https://protobuf.dev/programming-guides/editions/#updating

## Bugs and Feature Requests

Please file a go/turbo-ci-bug for any bugs or feature requests related to the
protobuf definitions in this repository.

## Turbo CI Data Model

The Turbo CI data model utilizes a graph of nodes to describe the work done when
a workflow is run.

### Core Concepts

*   **Workflow:** The high-level definition of the actions required to build,
    test, and validate software changes. A workflow functions as a "template"
    from which individual workplans can be instantiated. Workflows are specific
    to both a product (Chrome/Chromium, Android, etc.) and a role (presubmit,
    postsubmit, etc.), such as `Android presubmit`. Today Turbo CI does not
    store workflows so there is no Workflow proto definition, but that will be
    added later in 2026.
*   **Workplan:** A graph holding all nodes related to a single run of a
    workflow. See
    [graph/orchestrator/v1/workplan.proto](https://chromium.googlesource.com/infra/turboci/proto/+/refs/heads/main/turboci/graph/orchestrator/v1/workplan.proto).
*   **Checks:** Nodes representing work the workplan intends to accomplish,
    and the results of that work. Checks contain options (definition of the work
    to do) and results. Checks form the public API of the workplan, allowing
    the stages to be implementation details that typically don't need
    examination. See
    [graph/orchestrator/v1/check.proto](https://chromium.googlesource.com/infra/turboci/proto/+/refs/heads/main/turboci/graph/orchestrator/v1/check.proto).
*   **Stages:** Executable nodes managed by the Orchestrator, which will have
    their stage executor run them once all dependencies are satisfied. Whereas
    checks represent what to do, stages are a directive to actually do the work.
*   **Stage Attempts:** An attempt to run a stage, where a single stage may have
    more than one attempt due to retrying failures. See
    [graph/orchestrator/v1/stage.proto](https://chromium.googlesource.com/infra/turboci/proto/+/refs/heads/main/turboci/graph/orchestrator/v1/stage.proto).
*   **Stage Executors:** Services registered to execute specific stage types,
    based on the `type_url` of the stage's `args` field. Stage executors must run
    in Google's internal infrastructure, but it's possible to use GCP-hosted
    services via a Google-hosted proxy that invokes the GCP-hosted service.
    Such a proxy exists for LUCI Buildbucket, and can be added for other
    GCP-hosted services. See
    [graph/executor/v1/turbo_ci_stage_executor_service.proto](https://chromium.googlesource.com/infra/turboci/proto/+/refs/heads/main/turboci/graph/executor/v1/turbo_ci_stage_executor_service.proto).
    Googlers looking to maintain a stage executor can find more information at
    [go/turboci-stage-maintainers](http://go/turboci-stage-maintainers).

### Values (`Any`) & Decoupled Architecture

To cleanly separate the workplan's "skeleton" that the orchestrator needs to
operate on from workplan-specific data, Turbo CI encapsulates workplan-specific
payloads (Check Options, Check Results, Stage Args, and others) within protobuf
`Any` "Value" messages. Checks and Stages contain both non-Value content
(graph structure and other information the orchestrator directly uses) and Value
content (which is meaningful to the workplan, its stages, and its readers, but
can be opaque to the orchestrator).

Values are represented via a set of related protos, where different protos are
used when sending data to the orchestrator vs. when retrieving data from it:

*   **ValueWrite**: A message used to hold a Value when sending data to the
    orchestrator. See
    [graph/orchestrator/v1/value_write.proto](https://chromium.googlesource.com/infra/turboci/proto/+/refs/heads/main/turboci/graph/orchestrator/v1/value_write.proto).
*   **ValueRef**: Wraps/references a ValueData to embed it into a check, stage,
    or other message in the data model. Used when retrieving data from the
    orchestrator. ValueRefs retrieved from the orchestrator always store the
    Value's digest to allow the ValueData be looked up from the `value_data`
    map; the `inline` field is only used within the orchestrator. See
    [graph/orchestrator/v1/value_ref.proto](https://chromium.googlesource.com/infra/turboci/proto/+/refs/heads/main/turboci/graph/orchestrator/v1/value_ref.proto).
*   **ValueData**: A message used to hold a Value (or possibly a JSONPB-encoded
    version of it) when retrieving data from the orchestrator. Returned in a
    `value_data` map, keyed on the digest. Clients should typically use helper
    functions such as `value.Lookup()`
    ([Go](https://pkg.go.dev/go.chromium.org/luci/turboci/value#Lookup),
    [Python](https://chromium.googlesource.com/infra/turboci/proto/+/refs/heads/main/py/turboci/utils/value/decode.py#84))
    to access the Value content rather than interacting directly with ValueData
    messages. See
    [graph/orchestrator/v1/value_data.proto](https://chromium.googlesource.com/infra/turboci/proto/+/refs/heads/main/turboci/graph/orchestrator/v1/value_data.proto).

Encapsulating payloads in Value messages not only decouples the core
Orchestrator messages from workplan-specific messages, but also allows clients
to request only the specific Values they care about (avoiding unnecessary
proto dependencies) and allows the orchestrator to cleanly omit Value data that
a client doesn't have permission to access if they can see some but not all of
the content in a given check.

See [Repo layout](#repo-layout) for additional details.

### Turbo CI Lifecycles

The Turbo CI Orchestrator manages explicit, auditable state machines for Checks,
Stages, and Stage Attempts. In most cases the state transition graphs are
acyclic so there is no way to move from a later state to an earlier one, though
Stage Attempts can cycle between PENDING and THROTTLED repeatedly if necessary.

These are the three lifecycles in the Turbo CI data model:

*   [CheckState](https://chromium.googlesource.com/infra/turboci/proto/+/refs/heads/main/turboci/graph/orchestrator/v1/check_state.proto)
*   [StageState](https://chromium.googlesource.com/infra/turboci/proto/+/refs/heads/main/turboci/graph/orchestrator/v1/stage_state.proto)
*   [StageAttemptState](https://chromium.googlesource.com/infra/turboci/proto/+/refs/heads/main/turboci/graph/orchestrator/v1/stage_attempt_state.proto)

Lifecycle states for workplans will be added in the near future.
