#!/usr/bin/env vpython3

# Copyright 2025 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from __future__ import annotations

from pathlib import Path

import collections
import contextlib
import filecmp
import glob
import inspect
import os
import subprocess
import sys
import tempfile
import textwrap

from google.protobuf.descriptor_pb2  import FileDescriptorSet

from typing import Generator, NoReturn, Sequence

_RepoRoot = Path(__file__).absolute().parent

_env = os.environ.copy()
_env['PATH'] = os.path.pathsep.join((
  str((_RepoRoot / 'tools' / 'bin').absolute()),
  _env['PATH']))


def check_output(cmd: list[str|Path]) -> str|NoReturn:
  print(f"running: {' '.join(str(c) for c in cmd)}")
  p = subprocess.Popen(
      cmd,
      cwd=_RepoRoot, env=_env,
      stdout=subprocess.PIPE,
      stderr=sys.stderr, encoding='utf-8')
  out, _ = p.communicate(None)
  if p.returncode != 0:
    sys.exit(p.returncode)
  return out


def check_call(cmd: list[str|Path]):
  print(f"running: {' '.join(str(c) for c in cmd)}")
  ret = subprocess.call(cmd, cwd=_RepoRoot, env=_env)
  if ret != 0:
    sys.exit(ret)


def task_clean():
  """Removes all generated files."""
  print('cleaning go/**/*.pb.go')
  for file in quick_glob('go/**/*.pb.go'):
    os.remove(file)


def task_lint():
  """Runs `buf lint` on all protos in the current repo."""
  check_call(['buf', 'lint'])


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
  check_call(['buf', 'breaking', '--against', f'.git#ref={basis}'])


def protoc(*args: str):
  with tempfile.NamedTemporaryFile() as argfile:
    argfile.writelines((arg+'\n').encode() for arg in args)
    # include the whole repo as a proto path
    argfile.write(b'-I.\n')
    # compile all proto files under the turboci directory
    for file in quick_glob('turboci/**/*.proto'):
      argfile.write(file.encode())
      argfile.write(b'\n')
    argfile.flush()
    check_call(['protoc', f'@{argfile.name}'])


def quick_glob(pattern: str) -> list[str]:
  return glob.glob(pattern, root_dir=_RepoRoot, recursive=True)


def task_compile_desc(outfile: None|str = None):
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
    protoc('-o', tf.name)


def task_compile_go(mode: None|str = None):
  """Runs `protoc` to compile all Go stubs.

  If `mode` is `check`, then this will just check that the currently generated
  stubs are correct and will not write to disk.

  Example:
    build.py compile_go check
  """
  if mode not in (None, 'check'):
    print(f'compile_go: unknown mode={mode!r}')
    sys.exit(1)

  goRoot = _RepoRoot / 'go'

  # build to tempdir to implement mode=check
  with tempfile.TemporaryDirectory() as tdir:
    protoc(f'--go_out={tdir}', '--go_opt=module=go.chromium.org/turboci/proto/go')

    if not mode:
      task_clean()
      for file in glob.glob('**/*.pb.go', recursive=True, root_dir=tdir):
        print(file)
        os.rename(Path(tdir) / file, goRoot / file)
    elif mode == 'check':
      got = set(glob.glob('**/*.pb.go', recursive=True, root_dir=goRoot))
      want = set(glob.glob('**/*.pb.go', recursive=True, root_dir=tdir))

      report = {}

      report['missing in repo'] = want - got
      report['extra in repo'] = got - want
      _, report['with diff'], errs = filecmp.cmpfiles(
          goRoot, tdir, want.intersection(got), shallow=False)
      if errs:
        for err in errs:
          print('error for file', err)
        sys.exit(1)

      if all(not value for value in report.values()):
        return # ok!

      for category, files in sorted(report.items()):
        if files:
          print(f'{category}:')
          for file in files:
            print(f'  {file}')

      sys.exit(1)


def task_check_one_per_file():
  """Runs `protoc` to generate a descriptor, then ensures that every top-level
  type (Message, Enum, Extension) is unique within its .proto file.

  This is a best-practice check that we want to enforce for this repo.
  """
  fds = FileDescriptorSet()
  with tempfile.NamedTemporaryFile() as tf:
    task_compile_desc(tf.name)

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


def task_all():
  """Shorthand to run all presubmit checks."""
  fail = False

  for i, fn in enumerate((task_lint, task_breaking, task_check_one_per_file,
                          task_compile_go)):
    if i > 0:
      print()
    print(f'$ {sys.argv[0]} {fn.__name__.removeprefix("task_")}')
    try:
      fn()
      print('ok')
    except SystemExit:
      print('FAIL')
      fail = True

  if fail:
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
