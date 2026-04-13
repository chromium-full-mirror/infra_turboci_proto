#!/usr/bin/env vpython3

# Copyright 2025 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from __future__ import annotations

import collections
import contextlib
import filecmp
import glob
import gzip
import inspect
import os
import re
import subprocess
import sys
import tempfile
import textwrap

from pathlib import Path
from typing import NoReturn

from google.protobuf.descriptor_pb2 import (
    DescriptorProto,
    FieldDescriptorProto,
    FileDescriptorSet,
)

_RepoRoot = Path(__file__).absolute().parent

_env = os.environ.copy()
_env['PATH'] = os.path.pathsep.join(
    (str((_RepoRoot / 'tools' / 'bin').absolute()), _env['PATH'])
)


def check_output(cmd: list[str | Path]) -> str | NoReturn:
  print(f"running: {' '.join(str(c) for c in cmd)}")
  p = subprocess.Popen(
      cmd,
      cwd=_RepoRoot,
      env=_env,
      stdout=subprocess.PIPE,
      stderr=sys.stderr,
      encoding='utf-8',
  )
  out, _ = p.communicate(None)
  if p.returncode != 0:
    sys.exit(p.returncode)
  return out


def check_call(cmd: list[str | Path]):
  scmd: list[str] = [str(x) for x in cmd]
  if len(scmd) == 2 and scmd[0] == 'protoc' and scmd[1].startswith('@'):
    args = open(scmd[1][1:]).read()
    print(f"running: protoc {args}")
  else:
    print(f"running: {' '.join(str(c) for c in scmd)}")
  ret = subprocess.call(scmd, cwd=_RepoRoot, env=_env)
  if ret != 0:
    sys.exit(ret)


def task_clean():
  """Removes all generated files."""
  print('cleaning go/**/*.pb.go')
  for file in quick_glob('go/**/*.pb.go'):
    os.remove(_RepoRoot / file)
  for file in quick_glob('py/**/*_pb2.py*'):
    os.remove(_RepoRoot / file)


def task_format(mode: None | str = None):
  """Formats all proto files.

  If `mode` is `check`, then this will just check that the protos are correctly
  formatted and will not write to disk.

  Example:
    build.py format check
  """
  if mode not in (None, 'check'):
    print(f'format: unknown mode={mode!r}')
    sys.exit(1)

  if not mode:
    check_call(['buf', 'format', '-w'])
  else:
    delta = check_output(['buf', 'format', '-d'])
    if delta:
      print(delta)
      print()
      print(f'Fix formatting by running `{sys.argv[0]} format`.')
      sys.exit(1)


def task_lint():
  """Runs `buf lint` on all protos in the current repo."""
  check_call(['buf', 'lint'])


def task_breaking(basis: None | str = None):
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


def task_check_service_definitions():
  """Checks that there is a maximum of one service definition per package.

  Also checks that the file with that definition contains only the service, and
  no other top-level declarations.
  """
  with _fds() as fds:
    _task_check_service_definitions(fds)


def _task_check_service_definitions(desc: FileDescriptorSet):
  ok = True
  per_namespace: dict[str, set[str]] = {}
  for file in desc.file:
    if file.service:
      to_add = per_namespace.get(file.package)
      if not to_add:
        to_add = set()
        per_namespace[file.package] = to_add
      to_add.update(s.name for s in file.service)
      other_types = []
      for msg in file.message_type:
        other_types.append(f'message {msg.name}')
      for enum in file.enum_type:
        other_types.append(f'enum {enum.name}')
      for ext in file.extension:
        other_types.append(f'ext {ext.name}')
      if other_types:
        ok = False
        print(f'{file.name}: found other types along with service definition:')
        for typ in other_types:
          print(f'  {typ}')

  for ns, services in per_namespace.items():
    if len(services) > 1:
      ok = False
      print(f'namespace {ns!r} had multiple services:')
      for svc in services:
        print(f'  {svc!r}')

  if not ok:
    sys.exit(1)


def task_check_go_package():
  """Checks that go_package options make sense.

  Protos are always organized like:
    * turboci.dir...something.vX
    * the base of the go_package option must be (. replaced with /):
      go.chromium.org/turboci/proto/go/dir...vX:PKGNAME
    * PKGNAME must be `something` (the last component before the version)
    * for service protos:
        * the proto file's name must end with _service.proto.
        * the importpath must have an additional '/grpcpb' at the end.
        * the PKGNAME must have 'grpcpb' appended.
    * for non-service protos:
        * the proto file's name must NOT end with _service.proto.
  """
  with _fds() as fds:
    _task_check_go_package(fds)


_filenameRegex = re.compile(r'^turboci/(?:.*/)?([^/]*)/v[^/]*/(.*)\.proto$')


def _task_check_go_package(desc: FileDescriptorSet):
  ok = True
  for file in desc.file:
    mtch = _filenameRegex.match(file.name)
    if not mtch:
      print(f'bad filename {file.name}')
      ok = False
      continue

    pkgname, filename = mtch.group(1), mtch.group(2)

    expectPkg = file.package.removeprefix('turboci.').replace('.', '/')

    if bool(file.service):
      if not filename.endswith('_service'):
        print(f'{file.name}: bad filename: need _service suffix.')
      expectOption = f'{expectPkg}/grpcpb;{pkgname}grpcpb'
    else:
      if filename.endswith('_service'):
        print(f'{file.name}: bad filename: must not have _service suffix.')
      expectOption = f'{expectPkg};{pkgname}pb'
    expectOption = f'go.chromium.org/turboci/proto/go/{expectOption}'

    if (got := file.options.go_package) != expectOption:
      print(f'{file.name}: bad go_package {got!r}: wanted {expectOption!r}')
      ok = False

  if not ok:
    sys.exit(1)


def _check_message_fields(
    file_name: str, message: DescriptorProto, errors: list[str]
):
  """Recursively checks fields in a message and its nested types."""
  for field in message.field:
    # Check if the field is not repeated and not part of a oneof.
    # Note that map fields are also repeated fields.
    is_repeated = field.label == FieldDescriptorProto.Label.LABEL_REPEATED
    is_oneof = field.HasField('oneof_index')

    if not is_repeated and not is_oneof:
      # In proto3, the presence of `proto3_optional` means the `optional`
      # keyword was used.
      if not field.proto3_optional:
        errors.append(
            f'{file_name}: {message.name}.{field.name}: '
            'Non-repeated, non-oneof field must use the `optional` keyword.'
        )

  for nested_message in message.nested_type:
    if not nested_message.options.map_entry:
      _check_message_fields(file_name, nested_message, errors)


def _task_check_all_fields_optional(desc: FileDescriptorSet):
  """Checks that every non-repeated, non-oneof field uses the 'optional' keyword."""
  errors = []
  for file in desc.file:
    for message in file.message_type:
      _check_message_fields(file.name, message, errors)

  if errors:
    for error in errors:
      print(error)
    sys.exit(1)


def task_check_all_fields_optional():
  """Checks that every non-repeated, non-oneof field uses the 'optional' keyword."""
  with _fds() as fds:
    _task_check_all_fields_optional(fds)


def protoc(*args: str):
  with tempfile.NamedTemporaryFile() as argfile:
    argfile.writelines((arg + '\n').encode() for arg in args)
    # include the whole repo as a proto path
    argfile.write(b'-I.\n')
    # compile all proto files under the turboci directory
    for file in quick_glob('turboci/**/*.proto'):
      argfile.write(file.encode())
      argfile.write(b'\n')
    argfile.flush()
    check_call(['protoc', f'@{argfile.name}'])


def quick_glob(pattern: str) -> list[str]:
  return sorted(glob.glob(pattern, root_dir=_RepoRoot, recursive=True))


def task_compile_desc(outfile: None | str = None, include_imports: bool = False):
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
    args = ['-o', tf.name]
    if outfile:
      args += ['--retain_options', '--include_source_info']
    if include_imports:
      args += ['--include_imports']
    protoc(*args)


@contextlib.contextmanager
def _fds():
  fds = FileDescriptorSet()
  with tempfile.NamedTemporaryFile() as tf:
    task_compile_desc(tf.name)

    dat = tf.read()
    fds.MergeFromString(dat)
    yield fds


def _install_stubs(flavor: str, check: bool, src: Path, pattern: str, dst: Path):
  newFiles: list[str] = glob.glob(pattern, recursive=True, root_dir=src)

  if not check:
    for file in newFiles:
      print(f'{flavor}: {file}')
      target = dst / file
      os.makedirs(target.parent, exist_ok=True)
      os.rename(src / file, target)
    return

  got = set(glob.glob(pattern, recursive=True, root_dir=src))
  want = set(newFiles)

  report = {}

  report['missing in repo'] = want - got
  report['extra in repo'] = got - want
  _, report['with diff'], errs = filecmp.cmpfiles(
      dst, src, want.intersection(got), shallow=False
  )
  if errs:
    for err in errs:
      print('error for file', err)
    sys.exit(1)

  if all(not value for value in report.values()):
    return  # ok!

  relDst = dst.relative_to(_RepoRoot)
  for category, files in sorted(report.items()):
    if files:
      print(f'{category}:')
      for file in files:
        print(f'  {relDst}/{file}')

  sys.exit(1)


def task_compile_stubs(mode: None | str = None):
  """Runs `protoc` to compile all Go and Python stubs.

  If `mode` is `check`, then this will just check that the currently generated
  stubs are correct and will not write to disk.

  Example:
    build.py compile_stubs check
  """
  if mode not in (None, 'check'):
    print(f'compile_stubs: unknown mode={mode!r}')
    sys.exit(1)

  goModule = 'go.chromium.org/turboci/proto/go'

  # build to tempdir to implement mode=check
  with tempfile.TemporaryDirectory(dir=_RepoRoot) as tdir:
    tpth = Path(tdir)
    tgo = tpth/'go'
    tpy = tpth/'py'
    tgo.mkdir()
    tpy.mkdir()
    protoc(
        f'--go_out={tgo}',
        f'--go_opt=module={goModule}',
        f'--go-grpc_out={tgo}',
        f'--go-grpc_opt=module={goModule}',
        f'--go_opt=default_api_level=API_OPAQUE',
        f'--python_out={tpy}',
        f'--pyi_out={tpy}',
    )

    check = mode == 'check'
    if not check:
      task_clean()

    _install_stubs('go', check, tgo, '**/*.pb.go', _RepoRoot/'go')
    _install_stubs('py', check, tpy, '**/*.*', _RepoRoot/'py')


def task_store_descriptors(mode: None | str = None):
  """Runs `protoc` to store the transitive set of proto descriptors.

  If `mode` is `check`, then this will just check that the currently stored
  descriptors are correct.

  Example:
    build.py store_descriptors check
  """
  descPath = _RepoRoot / 'go' / 'utils' / 'turbocidesc' / 'desc.pb.gz'

  with tempfile.NamedTemporaryFile() as tf:
    task_compile_desc(tf.name, include_imports=True)
    raw = tf.read()
  gzipped = gzip.compress(raw, mtime=1)

  if mode == 'check':
    existing = open(descPath, 'rb').read()
    if existing != gzipped:
      print('stored descriptors bundle is out of date')
      sys.exit(1)
    return

  with open(descPath, 'wb') as f:
    f.write(gzipped)


def task_all():
  """Shorthand to run all presubmit checks."""
  fail = False

  with _fds() as fds:
    def check_service_definitions():
      _task_check_service_definitions(fds)

    def check_go_package():
      _task_check_go_package(fds)

    def check_all_fields_optional():
      _task_check_all_fields_optional(fds)

    allTasks = (
        task_format,
        check_service_definitions,
        check_go_package,
        check_all_fields_optional,
        task_lint,
        task_breaking,
        task_compile_stubs,
        task_store_descriptors,
    )

    for i, fn in enumerate(allTasks):
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
  tasks = {
      name.removeprefix('task_'): value
      for name, value in globals().items()
      if name.startswith('task_')
  }

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
