# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Helpers for extracting and manipulating ValueTags from proto messages."""

from __future__ import annotations

import collections.abc
import dataclasses
import typing

from google.protobuf import descriptor
from google.protobuf import message
from turboci import tag_pb2
from turboci.graph.orchestrator.v1 import tags_pb2
from turboci.utils.tags import extractor

__all__ = [
    'Map',
    'Tag',
    'field_tags',
    'for_message',
    'make',
]


def for_message(msg: message.Message | None) -> Map:
  """Extracts all TurboCI tags/data for the given message.

  Usually this is called automatically via `value.write`.

  Args:
    msg: The message to extract tags from.

  Returns:
    A Map dictionary with all extracted tags, or empty Map if none.
  """
  ret = Map()
  if msg is not None:
    ret.add(extractor.extract(msg))
  return ret


def field_tags(
    msg_or_type: (
        message.Message | type[message.Message] | descriptor.Descriptor
    ),
) -> collections.abc.Iterator[tuple[descriptor.FieldDescriptor, tag_pb2.Tag]]:
  """Yields field + normalized Tag protos for the given message type.

  This allows you to answer "If I used `for_message` on an instance of M, what
  tags could it contain?"

  Note: You can turn this into a dict with `dict(tags.field_tags(M))`.

  Args:
    msg_or_type: A Message instance, Message class, or message Descriptor.

  Yields:
    Tuples of (FieldDescriptor, normalized tag_pb2.Tag).
  """
  if isinstance(msg_or_type, descriptor.Descriptor):
    desc = msg_or_type
  else:
    desc = typing.cast(descriptor.Descriptor, msg_or_type.DESCRIPTOR)
  yield from extractor.field_tags(desc)


@dataclasses.dataclass(frozen=True, order=True)
class _TagValue:
  """An internal representation of a Tag.Value oneof (str, bool, or int)."""

  rank: int
  value: str | bool | int

  @classmethod
  def from_scalar(cls, value: str | bool | int) -> _TagValue:
    if isinstance(value, str):
      return cls(0, value)
    if isinstance(value, bool):
      return cls(1, value)
    if isinstance(value, int):
      return cls(2, value)
    raise TypeError(f'Unsupported _TagValue type: {type(value)}')

  def to_proto(
      self,
      indexed: bool = False,
      duplicate_count: int = 0,
  ) -> tags_pb2.Tag.Value:
    ret = tags_pb2.Tag.Value()
    if indexed:
      ret.indexed = True
    if duplicate_count > 0:
      ret.duplicate_count = duplicate_count
    if isinstance(self.value, str):
      ret.str_value = self.value
    elif isinstance(self.value, bool):
      ret.bool_value = self.value
    elif isinstance(self.value, int):
      ret.int_value = self.value
    else:
      raise ValueError(f'Unsupported _TagValue type: {type(self.value)}')
    return ret


def _make_tag_value(tv: tags_pb2.Tag.Value) -> _TagValue | None:
  which = tv.WhichOneof('data')
  if which == 'str_value':
    return _TagValue(0, tv.str_value)
  if which == 'bool_value':
    return _TagValue(1, tv.bool_value)
  if which == 'int_value':
    return _TagValue(2, tv.int_value)
  return None


@dataclasses.dataclass
class _ScopeCount:
  """Aggregates maximum observed `indexed` and instance count of a tag value."""

  indexed: bool = False
  count: int = 0

  def increment(self, indexed: bool, delta: int) -> None:
    self.indexed = max(self.indexed, indexed)
    self.count += delta


@dataclasses.dataclass
class Tag:
  """In-process representation of an orchestrator Tag."""

  indexed: bool = False
  _values: dict[_TagValue, _ScopeCount] = dataclasses.field(
      default_factory=dict
  )

  def values(self) -> list[tags_pb2.Tag.Value]:
    """Returns all Values contained in this Tag, in normalized order."""
    return [
        vt.to_proto(sc.indexed, sc.count - 1 if sc.count > 1 else 0)
        for vt, sc in sorted(self._values.items())
    ]

  def __contains__(self, value: object) -> bool:
    return self.has_value(value)[0] > 0

  def has_value(self, value: object) -> tuple[int, bool]:
    """Checks to see if this Tag contains the given value.

    Args:
      value: A Tag.Value (scope and duplicate_count ignored), str, bool, or int.

    Returns:
      Tuple of (total count, indexed?). If value is invalid or not in this tag,
      count is 0.
    """
    if isinstance(value, tags_pb2.Tag.Value):
      enc = _make_tag_value(value)
    elif isinstance(value, (str, bool, int)):
      enc = _TagValue.from_scalar(value)
    else:
      return (0, False)
    if enc is None or (got := self._values.get(enc)) is None:
      return (0, False)
    return (got.count, got.indexed)

  def add_value(
      self,
      value: tags_pb2.Tag.Value | str | bool | int,
      *,
      indexed: bool = False,
  ) -> None:
    """Inserts a value of the tag."""
    if isinstance(value, tags_pb2.Tag.Value):
      enc = _make_tag_value(value)
      if enc is None:
        return
      val_indexed = value.indexed
      delta = value.duplicate_count + 1
    else:
      enc = _TagValue.from_scalar(value)
      val_indexed = indexed
      delta = 1
    sc = self._values.setdefault(enc, _ScopeCount())
    sc.increment(val_indexed, delta)

  def to_proto(self, key: str) -> tags_pb2.Tag:
    """Returns this as a tags_pb2.Tag with the given key."""
    ret = tags_pb2.Tag(
        key=key,
        values=self.values(),
    )
    if self.indexed:
      ret.indexed = True
    return ret


class Map(dict[str, Tag]):
  """Dictionary mapping tag keys to Tag objects."""

  def __init__(self, *tags: tags_pb2.Tag) -> None:
    super().__init__()
    if tags:
      self.add(tags)

  @classmethod
  def make(cls, *tags: tags_pb2.Tag) -> Map:
    """Helper function to create a Map from Tag protos."""
    return cls(*tags)

  def to_proto(self) -> list[tags_pb2.Tag]:
    """Converts this Map into a normalized list of tags_pb2.Tag protos."""
    return [tag.to_proto(k) for k, tag in sorted(self.items())]

  def add(self, tags: collections.abc.Iterable[tags_pb2.Tag]) -> None:
    """Adds tag data in proto form from an iterable, merging identical keys."""
    for tag in tags:
      dat = self.setdefault(tag.key, Tag())
      dat.indexed = max(dat.indexed, tag.indexed)
      for value in tag.values:
        dat.add_value(value)


def make(
    key: str,
    *values: str | bool | int | tags_pb2.Tag.Value,
    indexed: bool = False,
    index_key_only: bool = False,
) -> tags_pb2.Tag:
  """Constructs a normalized Tag proto."""
  tg = Tag(indexed=indexed or index_key_only)
  for val in values:
    tg.add_value(val, indexed=indexed and not index_key_only)
  return tg.to_proto(key)
