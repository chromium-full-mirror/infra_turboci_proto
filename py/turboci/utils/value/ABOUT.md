# About `py/turboci/utils/value`

Last updated: 2026-05-28
Document current as of revision: 80d0c5d561191f92889c5641174d1f0b48e2db5d
Link: https://chromium.googlesource.com/infra/turboci/proto/+/80d0c5d561191f92889c5641174d1f0b48e2db5d

Note: There are no subdirectories in this path.

## Purpose
This directory handles data representation and access for ValueRefs that wrap
Protocol Buffer messages in Turbo CI workplan graphs. It provides utilities to:
*   Generate hash-based fingerprints (digests) for Protobuf messages.
*   Store, retrieve, and decode messages from data sources.
*   Lookup specific message types within ordered sequences of references.
*   Compare references and verify consistency during updates.

## Files

### `__init__.py`

Defines module-level constants and aggregates symbols from submodules. It
provides `TYPE_URL_PREFIX` and the `url()` function, which returns the full type
URL string for a given protobuf message class or instance.

### `absorb.py`

Processes `ValueRef` objects that hold raw inline data. The `absorb_inline`
function inspects a reference, calculates a SHA256 digest of its inline payload,
transforms that payload into a `ValueData`, stores it in a provided
`DataSource` using the digest as a key, updates the reference's `digest` field,
and clears the `inline` field on the reference.

### `data_source.py`

Defines interfaces (`DataSource`, `MutableDataSource`) and simple storage
implementations (like `SimpleDataSource`) for mapping digests to payloads. It
also contains `pick_data`, which helps a `DataSource` choose the most-complete
`ValueData` to store so JSON content can be accepted if it's computed after
binary content has already been stored.

### `decode.py`

Unpacks `ValueRef` objects back into usable runtime Protobuf objects. It
supports decoding inline data and resolving digest lookups from a `DataSource`.
It includes utilities for searching sorted lists of references (`lookup`) and
aggregating result lists specifically for `Check` proto objects (`results`).

### `digest.py`

Implements deterministic data fingerprinting for Protocol Buffer messages. It
contains the `Digest` class, which calculates SHA256 hashes for `Any` messages
and formats them as URL-safe Base64 strings, alongside helper routines for
predictable serialization and custom varint encoding.

### `match.py`

Provides functions (`write_matches_ref` and `ref_matches_ref`) to check if two
references point to the same underlying content. It ensures realms and message
types align and performs direct comparisons of the `digest` field, enforcing
the design guarantee that the `digest` field is always set on valid references.

### `ordered.py`

Maintains ordered lists of `ValueRef` objects sorted by `type_url`. It includes
utilities to locate references efficiently (`find`, `find_all`) and update
operations (`add_ref`, `set_ref`) that strictly preserve ordering and enforce
realm consistency.

### `refs_writes.py`

Contains factory functions for wrapping generic messages into persistent
transport containers. It includes `write()` to generate `ValueWrite` messages
and helpers to generate `ValueRef` objects (populating both the `inline`
payload and computed `digest` fields) while validating input conditions
and access constraints.
