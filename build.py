#!/usr/bin/env vpython3

# Copyright 2025 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from __future__ import annotations

from pathlib import Path

import collections
import contextlib
import glob
import inspect
import subprocess
import sys
import tempfile
import textwrap

from google.protobuf.descriptor_pb2  import FileDescriptorSet

from typing import NoReturn

_RepoRoot = Path(__file__).absolute().parent

_BinDir = _RepoRoot / 'tools' / 'bin'
_Buf = _BinDir / 'buf'
_Protoc = _BinDir / 'protoc'


def check_output(cmd: list[str|Path]) -> str|NoReturn:
  print(f"running: {' '.join(str(c) for c in cmd)}")
  p = subprocess.Popen(cmd, cwd=_RepoRoot, stdout=subprocess.PIPE,
                       stderr=sys.stderr, encoding='utf-8')
  out, _ = p.communicate(None)
  if p.returncode != 0:
    sys.exit(p.returncode)
  return out


def check_call(cmd: list[str|Path]):
  print(f"running: {' '.join(str(c) for c in cmd)}")
  ret = subprocess.call(cmd, cwd=_RepoRoot)
  if ret != 0:
    sys.exit(ret)


def task_lint():
  """Runs `buf lint` on all protos in the current repo."""
  check_call([_Buf, 'lint'])


def task_breaking(basis: None|str = None):
  """Runs `buf breaking` on all protos in the current repo.

  Uses base of the current branch as the reference to calculate breaking changes
  against. If you want a different reference, pass it as `basis` to this
  command.

  Example:
    build.py breaking HEAD~2
  """
  if basis is None:
    basis = check_output(['git', 'mark-merge-base']).split()[-1]
    if basis == 'None':
      # In a `bot_update` style checkout, mark-merge-base may return None.
      # In this context, HEAD~1 is correct because the CL was cherry-picked onto
      # the appropriate parent context (previous CL or current ref value).
      basis = 'HEAD~1'
  check_call([_Buf, 'breaking', '--against', f'.git#ref={basis}'])


def task_compile(outfile: None|str = None):
  """Runs `protoc` to ensure all protos can compile to a proto descriptor.

  The descriptor is discarded, unless outfile is provided.
  """
  if outfile is None:
    guardFn = tempfile.NamedTemporaryFile
  else:
    @contextlib.contextmanager
    def _guardFn():
      yield collections.namedtuple('fakeNamed', 'name')(outfile)
    guardFn = _guardFn

  with guardFn() as tf:
    with tempfile.NamedTemporaryFile() as argfile:
      argfile.writelines((file+'\n').encode() for file in glob.glob(
          'turboci/**/*.proto', root_dir=_RepoRoot, recursive=True,
      ))
      argfile.flush()
      check_call([_Protoc, '-I', '.', '-o', tf.name, f'@{argfile.name}'])


def task_check_one_per_file():
  """Runs `protoc` to generate a descriptor, then ensures that every top-level
  type (Message, Enum, Extension) is unique within its .proto file.

  This is a best-practice check that we want to enforce for this repo.
  """
  fds = FileDescriptorSet()
  with tempfile.NamedTemporaryFile() as tf:
    task_compile(tf.name)

    dat = tf.read()
    fds.MergeFromString(dat)

  failures = 0
  for file in fds.file:
    num_msgs = len(file.message_type)
    num_enums = len(file.enum_type)
    num_servs = len(file.service)
    num_exts = len(file.extension)
    total_top_level = num_msgs + num_enums + num_servs + num_exts
    if total_top_level > 1:
      failures += 1
      print(f'{file.name} had {total_top_level} top-level definitions (want 1):')
      for msg in file.message_type:
        print(f'  message {msg.name}')
      for enum in file.enum_type:
        print(f'  enum {enum.name}')
      for service in file.service:
        print(f'  service {service.name}')
      for ext in file.extension:
        print(f'  extend {ext.name}')
  if failures > 0:
    sys.exit(1)


def main(args: list[str]):
  # Note: this is probably too cute - if argument parsing ever gets more serious
  # than "subcommand with one additional optional positional argument", it would
  # be best to convert this to argparse.
  tasks = {name.removeprefix('task_'): value
           for name, value in globals().items()
           if name.startswith('task_')}

  def help() -> NoReturn:
    print(f'Usage: {sys.argv[0]} [cmd] [additional args...]')
    print()
    print('Commands:')
    for task, fn in sorted(tasks.items()):
      print()
      print(f'{task}{inspect.signature(fn)}:')
      print(textwrap.dedent(fn.__doc__.strip() or ''))
    sys.exit(1)

  if not args:
    help()

  cmd = args[0]
  fn = tasks.get(cmd)

  if fn is None:
    help()

  fn(*args[1:])
  print('ok')


if __name__ == '__main__':
  sys.exit(main(sys.argv[1:]))
