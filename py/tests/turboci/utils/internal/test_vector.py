# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Helper for running vectorized proto tests."""

from __future__ import annotations

import collections.abc
import pathlib
import typing
import unittest

from google.protobuf import message
from google.protobuf import text_format

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[5]
_VECTORS_ROOT = _REPO_ROOT / 'testing' / 'vectors'

_TestT = typing.TypeVar('_TestT', bound=message.Message)


def run(
    tc: unittest.TestCase,
    vectorsPath: str,
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
  resolved = _VECTORS_ROOT / vectorsPath
  tc.assertTrue(
      resolved.is_dir(),
      f'vectorsPath is not a valid test vector dir: {vectorsPath}.',
  )
  in_files = sorted(resolved.glob('*.textpb'))
  tc.assertTrue(in_files, f'no *.textpb files found in {resolved}')
  for in_path in in_files:
    base = in_path.name.removesuffix('.textpb')
    with tc.subTest(vector=base):
      cb(text_format.Parse(in_path.read_text(encoding='utf-8'), test_cls()))
