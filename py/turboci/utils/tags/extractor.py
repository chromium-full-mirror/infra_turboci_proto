# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Internal descriptor exploration and caching for tag extraction."""

from __future__ import annotations

import collections.abc
import dataclasses
import itertools
import threading
import typing

from google.protobuf import descriptor
from google.protobuf import descriptor_pb2
from google.protobuf import message
from turboci import tag_pb2
from turboci.graph.orchestrator.v1 import tags_pb2

_INT_FIELD_TYPES = {
    descriptor.FieldDescriptor.TYPE_INT32,
    descriptor.FieldDescriptor.TYPE_INT64,
    descriptor.FieldDescriptor.TYPE_SINT32,
    descriptor.FieldDescriptor.TYPE_SINT64,
    descriptor.FieldDescriptor.TYPE_SFIXED32,
    descriptor.FieldDescriptor.TYPE_SFIXED64,
    descriptor.FieldDescriptor.TYPE_FIXED32,
    descriptor.FieldDescriptor.TYPE_UINT32,
}

_ScalarValue: typing.TypeAlias = str | bool | int

_FieldValue: typing.TypeAlias = (
    _ScalarValue
    | collections.abc.Sequence[_ScalarValue]
    | message.Message
    | collections.abc.Sequence[message.Message]
    | collections.abc.Mapping[object, message.Message]
)


def _is_map_field(field: descriptor.FieldDescriptor) -> bool:
  return (
      field.type == descriptor.FieldDescriptor.TYPE_MESSAGE
      and field.message_type.GetOptions().map_entry
  )


def _is_list_field(field: descriptor.FieldDescriptor) -> bool:
  ismap = _is_map_field(field)  # pyright: ignore[reportAttributeAccessIssue]
  return field.is_repeated and not ismap


def _normalize_tag(
    tag: tag_pb2.Tag,
    field_type: int,
) -> tag_pb2.Tag:
  """Normalizes `tag` in accordance with field type and index rules.

  - indexed is set if index_key_only is True
  - capture_unset defaults to True for boolean fields
  - alt_key is sorted and deduplicated
  """
  tag_copy: tag_pb2.Tag | None = None

  def _get() -> tag_pb2.Tag:
    nonlocal tag_copy
    if tag_copy is None:
      tag_copy = tag_pb2.Tag()
      tag_copy.CopyFrom(tag)
    return tag_copy

  if tag.index_key_only:
    _get().indexed = True
  elif not tag.indexed:
    _get().ClearField('indexed')

  if (
      not tag.HasField('capture_unset')
      and field_type == descriptor.FieldDescriptor.TYPE_BOOL
  ):
    _get().capture_unset = True

  if any(a >= b for a, b in itertools.pairwise(tag.alt_key)):
    _get().alt_key[:] = sorted(set(tag.alt_key))

  return tag_copy if tag_copy is not None else tag


def _make_scalar_extractor(
    field: descriptor.FieldDescriptor,
) -> typing.Callable[[_ScalarValue, bool], list[tags_pb2.Tag.Value]] | None:
  if field.type == descriptor.FieldDescriptor.TYPE_ENUM:
    values_by_number = field.enum_type.values_by_number

    def _enum_extractor(
        v: _ScalarValue, indexed: bool
    ) -> list[tags_pb2.Tag.Value]:
      num = int(v)
      ev = values_by_number.get(num)
      name = ev.name if ev is not None else str(num)
      return [
          tags_pb2.Tag.Value(indexed=indexed, int_value=num),
          tags_pb2.Tag.Value(indexed=indexed, str_value=name),
      ]

    return _enum_extractor

  if field.type == descriptor.FieldDescriptor.TYPE_BOOL:
    return lambda v, indexed: [
        tags_pb2.Tag.Value(indexed=indexed, bool_value=bool(v))
    ]

  if field.type == descriptor.FieldDescriptor.TYPE_STRING:
    return lambda v, indexed: [
        tags_pb2.Tag.Value(indexed=indexed, str_value=str(v))
    ]

  if field.type in _INT_FIELD_TYPES:
    return lambda v, indexed: [
        tags_pb2.Tag.Value(indexed=indexed, int_value=int(v))
    ]

  return None


@dataclasses.dataclass
class _FieldExtractor:
  extract: typing.Callable[[_FieldValue], typing.Iterator[tags_pb2.Tag]]
  _: dataclasses.KW_ONLY
  capture_unset: bool = False
  tag: tag_pb2.Tag | None = None
  recurse_message: _MessageExtractor | None = None


class _MessageExtractor(dict[descriptor.FieldDescriptor, _FieldExtractor]):

  def __call__(self, msg: message.Message) -> typing.Iterator[tags_pb2.Tag]:
    for field, ext in self.items():
      if field.has_presence:
        if not ext.capture_unset and not msg.HasField(field.name):
          continue
        val = typing.cast(_FieldValue, getattr(msg, field.name))
      else:
        val = typing.cast(_FieldValue, getattr(msg, field.name))
        if not ext.capture_unset and not val:
          continue
      yield from ext.extract(val)


def _tagged_field_extractor(
    field: descriptor.FieldDescriptor,
    tag: tag_pb2.Tag,
) -> _FieldExtractor:
  if _is_map_field(field):
    raise ValueError(f'{field.full_name}: turboci.tag: unsupported field: map')

  codec = _make_scalar_extractor(field)
  if codec is None:
    kind_name = (
        descriptor_pb2.FieldDescriptorProto.Type.Name(field.type)
        .removeprefix('TYPE_')
        .lower()
    )
    raise ValueError(
        f'{field.full_name}: turboci.tag: unsupported field kind {kind_name}'
    )

  keys = (field.full_name, *tag.alt_key)
  indexed = tag.indexed
  index_key_only = tag.index_key_only
  capture_unset = tag.capture_unset
  is_list = _is_list_field(field)

  def _extract(val: _FieldValue) -> typing.Iterator[tags_pb2.Tag]:
    if is_list:
      items = typing.cast(collections.abc.Iterable[_ScalarValue], val)
    else:
      items = (typing.cast(_ScalarValue, val),)
    values = [
        tv for el in items for tv in codec(el, indexed and not index_key_only)
    ]
    for key in keys:
      yield tags_pb2.Tag(key=key, indexed=indexed, values=values)

  return _FieldExtractor(
      _extract,
      capture_unset=capture_unset,
      tag=tag,
  )


def _submsg_desc(
    field: descriptor.FieldDescriptor,
) -> descriptor.Descriptor | None:
  if _is_map_field(field):
    val_field = field.message_type.fields_by_name['value']
    if val_field.type == descriptor.FieldDescriptor.TYPE_MESSAGE:
      return val_field.message_type
    return None
  if field.type == descriptor.FieldDescriptor.TYPE_MESSAGE:
    return field.message_type
  return None


def _make_submsg_extractor(
    field: descriptor.FieldDescriptor,
    inner: _MessageExtractor,
) -> _FieldExtractor:
  if _is_map_field(field):

    def _extract(val: _FieldValue) -> typing.Iterator[tags_pb2.Tag]:
      mapping = typing.cast(
          collections.abc.Mapping[object, message.Message], val
      )
      for v in mapping.values():
        yield from inner(v)

  elif _is_list_field(field):

    def _extract(val: _FieldValue) -> typing.Iterator[tags_pb2.Tag]:
      seq = typing.cast(collections.abc.Iterable[message.Message], val)
      for v in seq:
        yield from inner(v)

  else:

    def _extract(val: _FieldValue) -> typing.Iterator[tags_pb2.Tag]:
      yield from inner(typing.cast(message.Message, val))

  return _FieldExtractor(_extract, recurse_message=inner)


_extractor_pool_lock = threading.Lock()
_extractor_pool: dict[descriptor.Descriptor, _MessageExtractor | Exception] = {}


def _explore_type(
    msg_desc: descriptor.Descriptor,
    to_add: dict[descriptor.Descriptor, _MessageExtractor],
    to_converge: dict[descriptor.FieldDescriptor, descriptor.Descriptor],
) -> None:
  """Recursively walks `msg_desc`, populating `to_add` with extractors.

  If a submessage field references a type still undergoing exploration, it is
  added to `to_converge` for subsequent cycle resolution.
  """
  if msg_desc in to_add:
    return

  fields = _MessageExtractor()
  to_add[msg_desc] = fields

  for field in msg_desc.fields:
    if field.GetOptions().HasExtension(tag_pb2.tag):
      tag_opt = _normalize_tag(
          field.GetOptions().Extensions[tag_pb2.tag], field.type
      )
      fields[field] = _tagged_field_extractor(field, tag_opt)
      continue

    sub_desc = _submsg_desc(field)
    if sub_desc is None:
      continue

    if sub_desc in _extractor_pool:
      cached = _extractor_pool[sub_desc]
      if isinstance(cached, Exception):
        raise cached
      if cached:
        fields[field] = _make_submsg_extractor(field, cached)
      continue

    _explore_type(sub_desc, to_add, to_converge)

    if ext := to_add.get(sub_desc):
      fields[field] = _make_submsg_extractor(field, ext)
    else:
      to_converge[field] = sub_desc


def _fixup_convergence(
    to_add: dict[descriptor.Descriptor, _MessageExtractor],
    to_converge: dict[descriptor.FieldDescriptor, descriptor.Descriptor],
) -> None:
  """Iterates through `to_converge` fixing up entries in `to_add`.

  Iterates until `to_converge` is empty or a full pass yields no changes.
  """
  did_something = True
  while did_something and to_converge:
    did_something = False
    for field in list(to_converge.keys()):
      sub_desc = to_converge[field]
      ext = to_add.get(sub_desc)
      if not ext:
        continue

      parent_desc = field.containing_type
      parent_extractor = to_add[parent_desc]
      parent_extractor[field] = _make_submsg_extractor(field, ext)
      did_something = True
      del to_converge[field]


def _compute_tag_extractor(
    msg_desc: descriptor.Descriptor,
) -> _MessageExtractor:
  if msg_desc in _extractor_pool:
    cached = _extractor_pool[msg_desc]
    if isinstance(cached, Exception):
      raise cached
    return cached

  to_add: dict[descriptor.Descriptor, _MessageExtractor] = {}
  to_converge: dict[descriptor.FieldDescriptor, descriptor.Descriptor] = {}

  try:
    _explore_type(msg_desc, to_add, to_converge)
    _fixup_convergence(to_add, to_converge)
    _extractor_pool.update(to_add)
    return to_add[msg_desc]
  except Exception as e:
    _extractor_pool[msg_desc] = e
    raise


def extract(msg: message.Message) -> typing.Iterator[tags_pb2.Tag]:
  """Extracts raw Tag protos from `msg`."""
  with _extractor_pool_lock:
    extractor = _compute_tag_extractor(
        typing.cast(descriptor.Descriptor, msg.DESCRIPTOR)
    )
  return extractor(msg)


def field_tags(
    msg_desc: descriptor.Descriptor,
) -> typing.Iterator[tuple[descriptor.FieldDescriptor, tag_pb2.Tag]]:
  """Yields (FieldDescriptor, tag_pb2.Tag) for reachable tagged fields."""
  try:
    with _extractor_pool_lock:
      te = _compute_tag_extractor(msg_desc)
  except Exception:  # pylint: disable=broad-exception-caught
    return

  visited: set[descriptor.Descriptor] = set()

  def _walk(
      desc: descriptor.Descriptor, ext: _MessageExtractor
  ) -> typing.Iterator[tuple[descriptor.FieldDescriptor, tag_pb2.Tag]]:
    if desc in visited:
      return
    visited.add(desc)
    for field, f_ext in ext.items():
      if f_ext.tag is not None:
        yield (field, f_ext.tag)
      elif f_ext.recurse_message is not None:
        sub_desc = _submsg_desc(field)
        if sub_desc is not None:
          yield from _walk(sub_desc, f_ext.recurse_message)

  yield from _walk(msg_desc, te)


def clear_cache_for_testing() -> None:
  """Clears the internal extractor cache. Only for use in unit tests."""
  with _extractor_pool_lock:
    _extractor_pool.clear()
