# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Helper for running vectorized proto tests."""

from __future__ import annotations

import collections.abc
import typing
import unittest
from base64 import b64decode

from google.protobuf import message
from google.protobuf import text_format

_TestT = typing.TypeVar("_TestT", bound=message.Message)


def run(
    tc: unittest.TestCase,
    vectors: dict[str, str],
    test_cls: type[_TestT],
    cb: collections.abc.Callable[[_TestT], None],
) -> None:
  """Discovers `<name>.textpb` and calls `cb`.

  Args:
    tc: The active TestCase instance used to create a subTest per vector.
    vectorsPath: Path to the vector directory (relative to
      `<repo_root>/testing/vectors`).
    test_cls: The proto Message class for `<name>.textpb`.
    cb: Callback invoked inside `tc.subTest(vector=<name>)` with `(input_pb,
      output_pb)`.
  """
  tc.assertTrue(vectors, "must supply at least one test vector")
  for name, vector in vectors.items():
    with tc.subTest(vector=name):
      cb(text_format.Parse(b64decode(vector), test_cls()))
