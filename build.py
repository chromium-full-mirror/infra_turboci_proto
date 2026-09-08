#!/usr/bin/env vpython3

# Copyright 2025 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Build is a helper script for performing all tasks in this repo.

Run it without arguments to find available tasks and their documentation.

Typically this is run as `build.py all` to do all the things.
"""

from __future__ import annotations

import ast
import collections
import contextlib
import filecmp
import glob
import gzip
import inspect
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import textwrap
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


def check_output(
    cmd: list[str | Path], *, cwd: Path = _RepoRoot
) -> str | NoReturn:
  print(f"running: {' '.join(str(c) for c in cmd)}")
  with subprocess.Popen(
      cmd,
      cwd=cwd,
      env=_env,
      stdout=subprocess.PIPE,
      stderr=sys.stderr,
      encoding='utf-8',
  ) as p:
    out, _ = p.communicate(None)
    if p.returncode != 0:
      sys.exit(p.returncode)
    return out


def check_call(cmd: list[str | Path], *, cwd: Path = _RepoRoot):
  scmd: list[str] = [str(x) for x in cmd]
  if len(scmd) == 2 and scmd[0] == 'protoc' and scmd[1].startswith('@'):
    with open(scmd[1][1:], encoding='utf-8') as args:
      print(f'running: protoc {args.read()}')
  else:
    print(f"running: {' '.join(str(c) for c in scmd)}")
  ret = subprocess.call(scmd, cwd=cwd, env=_env)
  if ret != 0:
    sys.exit(ret)


def _ensure_tools():
  check_call([
      'cipd',
      'ensure',
      '-root',
      _RepoRoot,
      '-ensure-file',
      _RepoRoot / 'tools.ensure',
  ])


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
      # In a `bot_update` style checkout, mark-merge-base may return
      # None. In this context, HEAD~1 is correct because the CL was
      # cherry-picked onto the appropriate parent context (previous CL or
      # current ref value).
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
    if not file.service:
      continue
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
    if not other_types:
      continue
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

# Files which do not need to have their go package restricted.
#
# The turboci/tag.proto is intentionally designed for minimal syntax; requiring
# it to have a package of `turboci.v1` just adds unnecessary noise, and the
# typical rational for this (needing to version these for service API
# versioning) does not apply.
_filenameGoPackageExceptions = frozenset([
    'turboci/tag.proto',
])


def _task_check_go_package(desc: FileDescriptorSet):
  ok = True
  for file in desc.file:
    if file.name in _filenameGoPackageExceptions:
      continue

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
        print(f'{file.name}: bad filename: has _service suffix.')
      expectOption = f'{expectPkg};{pkgname}pb'
    expectOption = f'go.chromium.org/turboci/proto/go/{expectOption}'

    if (got := file.options.go_package) != expectOption:
      print(f'{file.name}: bad go_package {got!r}: want {expectOption!r}')
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
            f'{file_name}: {message.name}.{field.name}: Non-repeated,'
            ' non-oneof field must use the `optional` keyword.'
        )

  for nested_message in message.nested_type:
    if not nested_message.options.map_entry:
      _check_message_fields(file_name, nested_message, errors)


def _task_check_all_fields_optional(desc: FileDescriptorSet):
  """Checks non-repeated, non-oneof fields uses the 'optional' keyword."""
  errors = []
  for file in desc.file:
    for message in file.message_type:
      _check_message_fields(file.name, message, errors)

  if errors:
    for error in errors:
      print(error)
    sys.exit(1)


def task_check_all_fields_optional():
  """Checks non-repeated, non-oneof fields uses the 'optional' keyword."""
  with _fds() as fds:
    _task_check_all_fields_optional(fds)


def _check_message_next_id(
    file_name: str,
    message: DescriptorProto,
    message_name: str,
    path: tuple[int, ...],
    cmap: dict[tuple[int, ...], str],
    errors: list[str],
):
  """Recursively checks 'Next ID' comments in a message and its children."""
  if path in cmap:
    comment = cmap[path]
    lines = [line.strip() for line in comment.splitlines() if line.strip()]
    if lines:
      last_line = lines[-1]
      if re.search(r'\bnext[_\s-]*id\b', last_line, re.IGNORECASE):
        numbers = [field.number for field in message.field] + [
            r.end - 1 for r in message.reserved_range
        ]
        expected_next_id = (max(numbers) + 1) if numbers else 1
        canonical_match = re.match(r'^Next ID:\s+(\d+)$', last_line)
        if canonical_match:
          comment_next_id = int(canonical_match.group(1))
          if comment_next_id != expected_next_id:
            errors.append(
                f'{file_name}: {message_name}: Next ID comment says'
                f' {comment_next_id}, but expected {expected_next_id}.'
            )
        else:
          errors.append(
              f'{file_name}: {message_name}: Non-canonical Next ID comment'
              f' {last_line!r}. Please use the canonical form "Next ID: XXX"'
              f' (e.g. "Next ID: {expected_next_id}").'
          )

  for i, nested_message in enumerate(message.nested_type):
    if not nested_message.options.map_entry:
      _check_message_next_id(
          file_name,
          nested_message,
          f'{message_name}.{nested_message.name}',
          path + (3, i),
          cmap,
          errors,
      )


def _task_check_next_id(desc: FileDescriptorSet):
  """Checks that 'Next ID' comment on messages matches expected next ID."""
  errors = []
  for file in desc.file:
    cmap = {}
    for loc in file.source_code_info.location:
      comments = []
      if loc.leading_comments:
        comments.append(loc.leading_comments)
      if loc.trailing_comments:
        comments.append(loc.trailing_comments)
      if loc.leading_detached_comments:
        comments.extend(loc.leading_detached_comments)
      if comments:
        cmap[tuple(loc.path)] = '\n'.join(comments)

    for i, message in enumerate(file.message_type):
      _check_message_next_id(
          file.name, message, message.name, (4, i), cmap, errors
      )

  if errors:
    for error in errors:
      print(error)
    sys.exit(1)


def task_check_next_id():
  """Checks that 'Next ID' comment on messages matches expected next ID."""
  with _fds() as fds:
    _task_check_next_id(fds)


def protoc(*args: str, include_testing=False):
  with tempfile.NamedTemporaryFile() as argfile:
    argfile.writelines((arg + '\n').encode() for arg in args)
    # include the whole repo as a proto path
    argfile.write(b'-I.\n')
    # compile all proto files under the turboci and testing directories
    for file in quick_glob('turboci/**/*.proto'):
      argfile.write(file.encode())
      argfile.write(b'\n')
    if include_testing:
      for file in quick_glob('testing/**/*.proto'):
        argfile.write(file.encode())
        argfile.write(b'\n')
    argfile.flush()
    check_call(['protoc', f'@{argfile.name}'])


def quick_glob(pattern: str) -> list[str]:
  return sorted(glob.glob(pattern, root_dir=_RepoRoot, recursive=True))


def task_compile_desc(
    outfile: None | str = None,
    include_imports: bool = False,
):
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


def _install_stubs(
    flavor: str, check: bool, src: Path, pattern: str, dst: Path
):
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
    tgo = tpth / 'go'
    tpy = tpth / 'py'
    tgo.mkdir()
    tpy.mkdir()
    protoc(
        f'--go_out={tgo}',
        f'--go_opt=module={goModule}',
        f'--go-grpc_out={tgo}',
        f'--go-grpc_opt=module={goModule}',
        '--go_opt=default_api_level=API_OPAQUE',
        f'--python_out={tpy}',
        f'--pyi_out={tpy}',
        include_testing=True,
    )

    check = mode == 'check'
    if not check:
      task_clean()

    _install_stubs('go', check, tgo, '**/*.pb.go', _RepoRoot / 'go')
    _install_stubs('py', check, tpy, '**/*.*', _RepoRoot / 'py')


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
    with open(descPath, 'rb') as existing:
      if existing.read() != gzipped:
        print('stored descriptors bundle is out of date')
        sys.exit(1)
      return

  with open(descPath, 'wb') as f:
    f.write(gzipped)


def task_check_python_imports():
  """Checks that Python files have only one import per import statement."""
  violations = False
  for rel_path in quick_glob('py/**/*.py'):
    if (
        rel_path.endswith('__init__.py')
        or rel_path.endswith('_pb2.py')
        or '/.' in rel_path
    ):
      continue
    abs_path = _RepoRoot / rel_path
    with open(abs_path, encoding='utf-8') as f:
      content = f.read()
    lines = content.splitlines()
    tree = ast.parse(content, rel_path)
    for node in ast.walk(tree):
      if isinstance(node, (ast.Import, ast.ImportFrom)):
        if getattr(node, 'module', None) == '__future__':
          continue
        if len(node.names) > 1:
          violations = True
          end_lineno = getattr(node, 'end_lineno', node.lineno)
          found = '\n'.join(lines[node.lineno - 1 : end_lineno])
          recommended = []
          if isinstance(node, ast.Import):
            for alias in node.names:
              if alias.asname:
                recommended.append(f'import {alias.name} as {alias.asname}')
              else:
                recommended.append(f'import {alias.name}')
          else:
            prefix = '.' * node.level + (node.module or '')
            for alias in node.names:
              if alias.asname:
                recommended.append(
                    f'from {prefix} import {alias.name} as {alias.asname}'
                )
              else:
                recommended.append(f'from {prefix} import {alias.name}')
          rec_str = '\n'.join(f'    {r}' for r in recommended)
          found_str = '\n'.join(f'    {line}' for line in found.splitlines())
          print(f'{rel_path}:{node.lineno}: multiple imports per statement')
          print('  Found:')
          print(found_str)
          print('  Recommended:')
          print(rec_str)
          print()

  if violations:
    sys.exit(1)


def task_test_python(verbose: None | str = None):
  """Runs python unittests."""
  args = [
      'vpython3',
      '-m',
      'unittest',
      'discover',
      '--buffer',
      '--locals',
      '--start-directory',
      _RepoRoot / 'py',
  ]
  if verbose in ('-v', '--verbose'):
    args.append('-v')
  check_call(args)


def task_install_venv_link():
  """Refreshes the `py/.venv` symlink."""
  link = _RepoRoot / 'py' / '.venv'
  link.unlink(missing_ok=True)
  link.symlink_to(sys.prefix, target_is_directory=True)


def task_test_go(verbose: None | str = None):
  """Runs python unittests."""
  args = ['go', 'test', 'go.chromium.org/turboci/proto/go/...']
  if verbose in ('-v', '--verbose'):
    args.append('-v')
  check_call(args, cwd=_RepoRoot / 'go')


def _clean_gclient_cruft():
  (_RepoRoot / '.gclient_entries').unlink(missing_ok=True)
  (_RepoRoot / '.gclient_previous_sync_commits').unlink(missing_ok=True)


def task_all():
  """Shorthand to run all presubmit checks."""
  fail = False

  # We used to have a .gclient spec embedded in this repo; clean up all the
  # cruft.
  _clean_gclient_cruft()

  with _fds() as fds:

    def check_service_definitions():
      _task_check_service_definitions(fds)

    def check_go_package():
      _task_check_go_package(fds)

    def check_all_fields_optional():
      _task_check_all_fields_optional(fds)

    def check_next_id():
      _task_check_next_id(fds)

    allTasks = (
        task_format,
        check_service_definitions,
        check_go_package,
        check_all_fields_optional,
        check_next_id,
        task_lint,
        task_breaking,
        task_compile_stubs,
        task_store_descriptors,
        task_check_python_imports,
        task_test_python,
        task_install_venv_link,
        task_test_go,
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
  # Note: this is probably too cute - if argument parsing ever gets more
  # serious than "subcommand with one additional optional positional
  # argument", it would be best to convert this to argparse.
  tasks = {
      name.removeprefix('task_'): value
      for name, value in globals().items()
      if name.startswith('task_')
  }

  def _help() -> NoReturn:
    print(f'Usage: {sys.argv[0]} [cmd] [additional args...]')
    print()
    print('Commands:')
    for task, fn in sorted(tasks.items()):
      print()
      print(f'{task}{inspect.signature(fn)}:')
      print(textwrap.dedent(fn.__doc__.strip() or ''))
    sys.exit(1)

  if not args:
    _help()

  cmd = args[0]
  fn = tasks.get(cmd)

  if fn is None:
    _help()

  _ensure_tools()

  fn(*args[1:])
  print('ok')


if __name__ == '__main__':
  sys.exit(main(sys.argv[1:]))
