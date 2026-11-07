# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Tests for turboci.utils.tags."""

import typing
import unittest

from google.protobuf import descriptor_pb2
from google.protobuf import descriptor_pool
from google.protobuf import empty_pb2
from google.protobuf import message
from google.protobuf import message_factory

from testing.tags import demo_pb2
from testing.vectors.tags.tags_for import test_case_pb2
from tests.turboci.utils.internal import test_vector
from tests.turboci.utils.tags.test_for_tags_vectors import _TAGS_FOR_VECTORS
from turboci import tag_pb2
from turboci.graph.orchestrator.v1 import tags_pb2
from turboci.utils import tags
from turboci.utils.tags import extractor


class TestForMessage(unittest.TestCase):
  _dyn_pool: descriptor_pool.DescriptorPool

  @classmethod
  def setUpClass(cls) -> None:
    super().setUpClass()
    cls._dyn_pool = descriptor_pool.DescriptorPool()
    for mod in (
        descriptor_pb2,
        empty_pb2,
        tag_pb2,
        demo_pb2,
        tags_pb2,
        test_case_pb2,
    ):
      fdp = descriptor_pb2.FileDescriptorProto()
      mod.DESCRIPTOR.CopyToProto(fdp)
      cls._dyn_pool.Add(fdp)

  def _to_dynamic(self, msg: message.Message) -> message.Message:
    desc = self._dyn_pool.FindMessageTypeByName(msg.DESCRIPTOR.full_name)
    dyn_cls = message_factory.GetMessageClass(desc)
    dyn_msg = dyn_cls()
    dyn_msg.ParseFromString(msg.SerializeToString())
    return dyn_msg

  def test_vectors(self):
    def _check(tc: test_case_pb2.TagsFor) -> None:
      which = tc.input.WhichOneof('msg')
      if which is None:
        msg: message.Message | None = None
        dyn_msg: message.Message | None = None
      else:
        msg = typing.cast(message.Message, getattr(tc.input, which))
        dyn_msg = self._to_dynamic(msg)

      for label, target in (
          ('static desc pool', msg),
          ('dynamic desc pool', dyn_msg),
      ):
        with self.subTest(pool=label):
          if tc.output.HasField('error'):
            with self.assertRaises(ValueError) as cm:
              tags.for_message(target)
            self.assertIn(tc.output.error, str(cm.exception))
          else:
            got = tags.for_message(target)
            self.assertEqual(got.to_proto(), list(tc.output.tag))

    test_vector.run(self, _TAGS_FOR_VECTORS, test_case_pb2.TagsFor, _check)

  def test_tags_for_convergence(self):
    msg = demo_pb2.LoopMessageD(
        tagged='d_root',
        deeper=demo_pb2.LoopMessageA(
            deeper=demo_pb2.LoopMessageB(
                deeper=demo_pb2.LoopMessageC(
                    deeper=demo_pb2.LoopMessageD(
                        tagged='d_nested',
                    ),
                ),
            ),
        ),
    )
    want = tags.Map(
        tags.make('testing.tags.LoopMessageD.tagged', 'd_nested', 'd_root'),
    )
    for _ in range(10):
      extractor.clear_cache_for_testing()
      self.assertEqual(tags.for_message(msg), want)


class TestTagsProto(unittest.TestCase):

  def test_basic(self):
    protos = tags.Map(
        tags.make(
            'my.tag',
            'val1',
            'val1',
            42,
            index_key_only=True,
        ),
    ).to_proto()
    self.assertEqual(len(protos), 1)
    self.assertEqual(
        protos[0],
        tags_pb2.Tag(
            key='my.tag',
            indexed=True,
            values=[
                tags_pb2.Tag.Value(
                    duplicate_count=1,
                    str_value='val1',
                ),
                tags_pb2.Tag.Value(
                    int_value=42,
                ),
            ],
        ),
    )

  def test_strings_sorted_lexicographically(self):
    protos = tags.Map(
        tags.make(
            'my.tag',
            'zebra',
            '',
            'banana',
            'apple',
            'banana',
            index_key_only=True,
        ),
    ).to_proto()
    self.assertEqual(len(protos), 1)
    self.assertEqual(
        protos[0],
        tags_pb2.Tag(
            key='my.tag',
            indexed=True,
            values=[
                tags_pb2.Tag.Value(str_value=''),
                tags_pb2.Tag.Value(str_value='apple'),
                tags_pb2.Tag.Value(duplicate_count=1, str_value='banana'),
                tags_pb2.Tag.Value(str_value='zebra'),
            ],
        ),
    )

  def test_booleans_false_before_true(self):
    protos = tags.Map(
        tags.make(
            'my.tag',
            True,
            False,
            True,
            index_key_only=True,
        ),
    ).to_proto()
    self.assertEqual(len(protos), 1)
    self.assertEqual(
        protos[0],
        tags_pb2.Tag(
            key='my.tag',
            indexed=True,
            values=[
                tags_pb2.Tag.Value(bool_value=False),
                tags_pb2.Tag.Value(duplicate_count=1, bool_value=True),
            ],
        ),
    )

  def test_integers_sorted_numerically(self):
    protos = tags.Map(
        tags.make(
            'my.tag',
            42,
            -100,
            0,
            10,
            -100,
            index_key_only=True,
        ),
    ).to_proto()
    self.assertEqual(len(protos), 1)
    self.assertEqual(
        protos[0],
        tags_pb2.Tag(
            key='my.tag',
            indexed=True,
            values=[
                tags_pb2.Tag.Value(duplicate_count=1, int_value=-100),
                tags_pb2.Tag.Value(int_value=0),
                tags_pb2.Tag.Value(int_value=10),
                tags_pb2.Tag.Value(int_value=42),
            ],
        ),
    )

  def test_mixed_type_ordering(self):
    protos = tags.Map(
        tags.make(
            'my.tag',
            100,
            -5,
            0,
            'zebra',
            'apple',
            'apple',
            True,
            False,
            indexed=True,
        ),
    ).to_proto()
    self.assertEqual(len(protos), 1)
    self.assertEqual(
        protos[0],
        tags_pb2.Tag(
            key='my.tag',
            indexed=True,
            values=[
                tags_pb2.Tag.Value(
                    indexed=True, duplicate_count=1, str_value='apple'
                ),
                tags_pb2.Tag.Value(indexed=True, str_value='zebra'),
                tags_pb2.Tag.Value(indexed=True, bool_value=False),
                tags_pb2.Tag.Value(indexed=True, bool_value=True),
                tags_pb2.Tag.Value(indexed=True, int_value=-5),
                tags_pb2.Tag.Value(indexed=True, int_value=0),
                tags_pb2.Tag.Value(indexed=True, int_value=100),
            ],
        ),
    )

  def test_keys_sorted_lexicographically(self):
    protos = tags.Map(
        tags.make('z.tag', '1'),
        tags.make('a.tag', '2'),
        tags.make('m.tag', '3'),
    ).to_proto()
    self.assertEqual([p.key for p in protos], ['a.tag', 'm.tag', 'z.tag'])


class TestTagMethods(unittest.TestCase):

  def test_has_value(self):
    t = tags.Tag(indexed=True)
    t.add_value(
        tags_pb2.Tag.Value(indexed=False, str_value='hello', duplicate_count=2)
    )
    self.assertIn('hello', t)
    self.assertNotIn('missing', t)
    self.assertEqual(t.has_value('hello'), (3, False))
    self.assertEqual(
        t.has_value(tags_pb2.Tag.Value(indexed=True, str_value='hello')),
        (3, False),
    )
    self.assertEqual(t.has_value('missing'), (0, False))
    self.assertEqual(t.has_value(tags_pb2.Tag.Value()), (0, False))
    self.assertEqual(t.has_value(123), (0, False))

  def test_add_value_merges_scope_and_duplicate_count(self):
    t = tags.Tag()
    t.add_value(
        tags_pb2.Tag.Value(indexed=False, int_value=42, duplicate_count=1)
    )
    t.add_value(
        tags_pb2.Tag.Value(indexed=True, int_value=42, duplicate_count=2)
    )
    t.add_value(42, indexed=False)
    self.assertEqual(t.has_value(42), (6, True))
    vals = t.values()
    self.assertEqual(len(vals), 1)
    self.assertEqual(vals[0].duplicate_count, 5)
    self.assertEqual(vals[0].indexed, True)


class TestMetadata(unittest.TestCase):

  def _assert_field_tags(
      self,
      msg_type: type[message.Message],
      want: dict[str, tag_pb2.Tag],
  ) -> None:
    got = {f.full_name: t for f, t in tags.field_tags(msg_type)}
    self.assertEqual(got, want)

  def test_my_message(self):
    self._assert_field_tags(
        demo_pb2.MyMessage,
        {
            'testing.tags.MyMessage.tagged_field': tag_pb2.Tag(),
        },
    )

  def test_complex_message(self):
    self._assert_field_tags(
        demo_pb2.ComplexMessage,
        {
            'testing.tags.ComplexMessage.SubMessage.sub_tagged': tag_pb2.Tag(
                alt_key=['previous.package.name.Message.field'],
            ),
            'testing.tags.ComplexMessage.local_str': tag_pb2.Tag(),
            'testing.tags.ComplexMessage.workplan_str': tag_pb2.Tag(
                indexed=True,
            ),
            'testing.tags.ComplexMessage.local_bool': tag_pb2.Tag(
                capture_unset=True,
            ),
            'testing.tags.ComplexMessage.local_enum': tag_pb2.Tag(),
            'testing.tags.ComplexMessage.rep_str': tag_pb2.Tag(),
            'testing.tags.ComplexMessage.split_index': tag_pb2.Tag(
                indexed=True,
                index_key_only=True,
            ),
            'testing.tags.ComplexMessage.explicit_presence_bool': tag_pb2.Tag(
                capture_unset=False,
            ),
        },
    )

  def test_unsupported_kind_message(self):
    self._assert_field_tags(demo_pb2.UnsupportedKindMessage, {})

  def test_recursive_message(self):
    self._assert_field_tags(
        demo_pb2.RecursiveMessage,
        {
            'testing.tags.RecursiveMessage.tagged': tag_pb2.Tag(),
        },
    )

  def test_loop_message_d(self):
    self._assert_field_tags(
        demo_pb2.LoopMessageD,
        {
            'testing.tags.LoopMessageD.tagged': tag_pb2.Tag(),
        },
    )


if __name__ == '__main__':
  unittest.main()
