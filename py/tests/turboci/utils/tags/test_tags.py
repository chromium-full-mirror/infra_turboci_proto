# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Tests for turboci.utils.tags."""

import unittest

from google.protobuf import descriptor_pb2
from google.protobuf import descriptor_pool
from google.protobuf import empty_pb2
from google.protobuf import message
from google.protobuf import message_factory
from testing.tags import demo_pb2
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
    for mod in (descriptor_pb2, empty_pb2, tag_pb2, demo_pb2):
      fdp = descriptor_pb2.FileDescriptorProto()
      mod.DESCRIPTOR.CopyToProto(fdp)
      cls._dyn_pool.Add(fdp)

  def _to_dynamic(self, msg: message.Message) -> message.Message:
    desc = self._dyn_pool.FindMessageTypeByName(msg.DESCRIPTOR.full_name)
    dyn_cls = message_factory.GetMessageClass(desc)
    dyn_msg = dyn_cls()
    dyn_msg.ParseFromString(msg.SerializeToString())
    return dyn_msg

  def _assert_tags(
      self,
      msg: message.Message,
      want: tags.Map,
  ) -> None:
    for label, target in (
        ('static desc pool', msg),
        ('dynamic desc pool', self._to_dynamic(msg)),
    ):
      with self.subTest(pool=label):
        self.assertEqual(tags.for_message(target), want)

  def test_nil(self):
    self.assertDictEqual(tags.for_message(None), {})

  def test_empty(self):
    self._assert_tags(empty_pb2.Empty(), tags.Map())

  def test_untagged_field(self):
    msg = demo_pb2.MyMessage(untagged_field='hello')
    self._assert_tags(msg, tags.Map())

  def test_tagged_field(self):
    msg = demo_pb2.MyMessage(tagged_field='hello')
    self._assert_tags(
        msg,
        tags.Map(
            tags.make('testing.tags.MyMessage.tagged_field', 'hello'),
        ),
    )

  def test_complex_message_local_str(self):
    msg = demo_pb2.ComplexMessage(local_str='foo')
    self._assert_tags(
        msg,
        tags.Map(
            tags.make('testing.tags.ComplexMessage.local_str', 'foo'),
            tags.make('testing.tags.ComplexMessage.local_bool', False),
        ),
    )

  def test_complex_message_workplan_str(self):
    msg = demo_pb2.ComplexMessage(workplan_str='foo')
    self._assert_tags(
        msg,
        tags.Map(
            tags.make(
                'testing.tags.ComplexMessage.workplan_str',
                'foo',
                indexed=True,
            ),
            tags.make('testing.tags.ComplexMessage.local_bool', False),
        ),
    )

  def test_complex_message_local_bool_true(self):
    msg = demo_pb2.ComplexMessage(local_bool=True)
    self._assert_tags(
        msg,
        tags.Map(
            tags.make('testing.tags.ComplexMessage.local_bool', True),
        ),
    )

  def test_complex_message_local_bool_unset(self):
    msg = demo_pb2.ComplexMessage()
    self._assert_tags(
        msg,
        tags.Map(
            tags.make('testing.tags.ComplexMessage.local_bool', False),
        ),
    )

  def test_complex_message_explicit_presence_bool_unset(self):
    msg = demo_pb2.ComplexMessage()
    self._assert_tags(
        msg,
        tags.Map(
            tags.make('testing.tags.ComplexMessage.local_bool', False),
        ),
    )

  def test_complex_message_explicit_presence_bool_false(self):
    msg = demo_pb2.ComplexMessage(explicit_presence_bool=False)
    self._assert_tags(
        msg,
        tags.Map(
            tags.make('testing.tags.ComplexMessage.local_bool', False),
            tags.make(
                'testing.tags.ComplexMessage.explicit_presence_bool', False
            ),
        ),
    )

  def test_complex_message_explicit_presence_bool_true(self):
    msg = demo_pb2.ComplexMessage(explicit_presence_bool=True)
    self._assert_tags(
        msg,
        tags.Map(
            tags.make('testing.tags.ComplexMessage.local_bool', False),
            tags.make(
                'testing.tags.ComplexMessage.explicit_presence_bool', True
            ),
        ),
    )

  def test_complex_message_local_enum(self):
    msg = demo_pb2.ComplexMessage(local_enum=demo_pb2.TEST_ENUM_ONE)
    self._assert_tags(
        msg,
        tags.Map(
            tags.make(
                'testing.tags.ComplexMessage.local_enum', 'TEST_ENUM_ONE', 1
            ),
            tags.make('testing.tags.ComplexMessage.local_bool', False),
        ),
    )

  def test_complex_message_rep_str(self):
    msg = demo_pb2.ComplexMessage(rep_str=['c', 'a', 'b', 'a'])
    want = tags.Map(
        tags.make('testing.tags.ComplexMessage.rep_str', 'a', 'a', 'b', 'c'),
        tags.make('testing.tags.ComplexMessage.local_bool', False),
    )
    self._assert_tags(msg, want)
    res = tags.for_message(msg)
    count, indexed = res['testing.tags.ComplexMessage.rep_str'].has_value('a')
    self.assertEqual(count, 2)
    self.assertEqual(indexed, False)

  def test_complex_message_map_sub(self):
    msg = demo_pb2.ComplexMessage()
    msg.map_sub['k1'].sub_tagged = 'sub1'
    msg.map_sub['k2'].sub_tagged = 'sub2'
    msg.map_sub['k3'].sub_tagged = 'sub1'
    self._assert_tags(
        msg,
        tags.Map(
            tags.make(
                'testing.tags.ComplexMessage.SubMessage.sub_tagged',
                'sub1',
                'sub1',
                'sub2',
            ),
            tags.make(
                'previous.package.name.Message.field',
                'sub1',
                'sub1',
                'sub2',
            ),
            tags.make('testing.tags.ComplexMessage.local_bool', False),
        ),
    )

  def test_complex_message_rep_sub(self):
    msg = demo_pb2.ComplexMessage()
    msg.rep_sub.append(demo_pb2.ComplexMessage.SubMessage(sub_tagged='sub1'))
    msg.rep_sub.append(demo_pb2.ComplexMessage.SubMessage(sub_tagged='sub2'))
    msg.rep_sub.append(demo_pb2.ComplexMessage.SubMessage(sub_tagged='sub1'))
    self._assert_tags(
        msg,
        tags.Map(
            tags.make(
                'testing.tags.ComplexMessage.SubMessage.sub_tagged',
                'sub1',
                'sub1',
                'sub2',
            ),
            tags.make(
                'previous.package.name.Message.field',
                'sub1',
                'sub1',
                'sub2',
            ),
            tags.make('testing.tags.ComplexMessage.local_bool', False),
        ),
    )

  def test_complex_message_sub(self):
    msg = demo_pb2.ComplexMessage(
        sub=demo_pb2.ComplexMessage.SubMessage(sub_tagged='hi')
    )
    self._assert_tags(
        msg,
        tags.Map(
            tags.make(
                'testing.tags.ComplexMessage.SubMessage.sub_tagged', 'hi'
            ),
            tags.make('previous.package.name.Message.field', 'hi'),
            tags.make('testing.tags.ComplexMessage.local_bool', False),
        ),
    )

  def test_complex_message_split_index(self):
    msg = demo_pb2.ComplexMessage(split_index=123)
    self._assert_tags(
        msg,
        tags.Map(
            tags.make(
                'testing.tags.ComplexMessage.split_index',
                123,
                index_key_only=True,
            ),
            tags.make('testing.tags.ComplexMessage.local_bool', False),
        ),
    )

  def test_complex_message_multiple(self):
    msg = demo_pb2.ComplexMessage(
        local_str='foo',
        workplan_str='wp',
        local_bool=False,
        local_enum=demo_pb2.TEST_ENUM_ONE,
        rep_str=['c', 'a', 'b', 'a'],
        sub=demo_pb2.ComplexMessage.SubMessage(sub_tagged='single'),
        split_index=123,
    )
    msg.map_sub['k1'].sub_tagged = 'sub1'
    msg.map_sub['k2'].sub_tagged = 'sub2'
    msg.rep_sub.append(demo_pb2.ComplexMessage.SubMessage(sub_tagged='rep1'))
    msg.rep_sub.append(demo_pb2.ComplexMessage.SubMessage(sub_tagged='rep2'))

    self._assert_tags(
        msg,
        tags.Map(
            tags.make('testing.tags.ComplexMessage.local_str', 'foo'),
            tags.make(
                'testing.tags.ComplexMessage.workplan_str', 'wp', indexed=True
            ),
            tags.make('testing.tags.ComplexMessage.local_bool', False),
            tags.make(
                'testing.tags.ComplexMessage.local_enum', 'TEST_ENUM_ONE', 1
            ),
            tags.make(
                'testing.tags.ComplexMessage.rep_str', 'a', 'a', 'b', 'c'
            ),
            tags.make(
                'testing.tags.ComplexMessage.split_index',
                123,
                index_key_only=True,
            ),
            tags.make(
                'testing.tags.ComplexMessage.SubMessage.sub_tagged',
                'rep1',
                'rep2',
                'single',
                'sub1',
                'sub2',
            ),
            tags.make(
                'previous.package.name.Message.field',
                'rep1',
                'rep2',
                'single',
                'sub1',
                'sub2',
            ),
        ),
    )

  def test_unsupported_kind(self):
    msg = demo_pb2.UnsupportedKindMessage(bad_field=b'bad')
    for label, target in (
        ('static desc pool', msg),
        ('dynamic desc pool', self._to_dynamic(msg)),
    ):
      with self.subTest(pool=label):
        with self.assertRaisesRegex(
            ValueError,
            r'testing\.tags\.UnsupportedKindMessage\.bad_field: turboci\.tag:'
            r' unsupported field kind bytes',
        ):
          tags.for_message(target)

  def test_recursive_message(self):
    msg = demo_pb2.RecursiveMessage(
        tagged='root',
        deeper=demo_pb2.RecursiveMessage(
            tagged='level1',
            deeper=demo_pb2.RecursiveMessage(
                tagged='level2',
            ),
        ),
    )
    self._assert_tags(
        msg,
        tags.Map(
            tags.make(
                'testing.tags.RecursiveMessage.tagged',
                'level1',
                'level2',
                'root',
            ),
        ),
    )

  def test_recursive_untagged_message(self):
    msg = demo_pb2.RecursiveUntaggedMessage(
        untagged='root',
        deeper=demo_pb2.RecursiveUntaggedMessage(
            untagged='level1',
            deeper=demo_pb2.RecursiveUntaggedMessage(
                untagged='level2',
            ),
        ),
    )
    self._assert_tags(msg, tags.Map())

  def test_mutual_message_a_with_nested_tags(self):
    msg = demo_pb2.MutualMessageA(
        deeper=demo_pb2.MutualMessageB(
            tagged='b_level1',
            deeper=demo_pb2.MutualMessageA(
                deeper=demo_pb2.MutualMessageB(
                    tagged='b_level2',
                ),
            ),
        ),
    )
    self._assert_tags(
        msg,
        tags.Map(
            tags.make(
                'testing.tags.MutualMessageB.tagged', 'b_level1', 'b_level2'
            ),
        ),
    )

  def test_mutual_message_b_with_nested_tags(self):
    msg = demo_pb2.MutualMessageB(
        tagged='b_root',
        deeper=demo_pb2.MutualMessageA(
            deeper=demo_pb2.MutualMessageB(
                tagged='b_nested',
            ),
        ),
    )
    self._assert_tags(
        msg,
        tags.Map(
            tags.make(
                'testing.tags.MutualMessageB.tagged', 'b_nested', 'b_root'
            ),
        ),
    )

  def test_mutual_untagged_message_a(self):
    msg = demo_pb2.MutualUntaggedMessageA(
        deeper=demo_pb2.MutualUntaggedMessageB(
            untagged='level1',
            deeper=demo_pb2.MutualUntaggedMessageA(
                deeper=demo_pb2.MutualUntaggedMessageB(
                    untagged='level2',
                ),
            ),
        ),
    )
    self._assert_tags(msg, tags.Map())

  def test_mutual_untagged_message_b(self):
    msg = demo_pb2.MutualUntaggedMessageB(
        untagged='level1',
        deeper=demo_pb2.MutualUntaggedMessageA(
            deeper=demo_pb2.MutualUntaggedMessageB(
                untagged='level2',
            ),
        ),
    )
    self._assert_tags(msg, tags.Map())

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
                    indexed=False,
                    duplicate_count=1,
                    str_value='val1',
                ),
                tags_pb2.Tag.Value(
                    indexed=False,
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
                tags_pb2.Tag.Value(indexed=False, str_value=''),
                tags_pb2.Tag.Value(indexed=False, str_value='apple'),
                tags_pb2.Tag.Value(
                    indexed=False, duplicate_count=1, str_value='banana'
                ),
                tags_pb2.Tag.Value(indexed=False, str_value='zebra'),
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
                tags_pb2.Tag.Value(indexed=False, bool_value=False),
                tags_pb2.Tag.Value(
                    indexed=False, duplicate_count=1, bool_value=True
                ),
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
                tags_pb2.Tag.Value(
                    indexed=False, duplicate_count=1, int_value=-100
                ),
                tags_pb2.Tag.Value(indexed=False, int_value=0),
                tags_pb2.Tag.Value(indexed=False, int_value=10),
                tags_pb2.Tag.Value(indexed=False, int_value=42),
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
