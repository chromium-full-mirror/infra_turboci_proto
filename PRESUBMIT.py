# Copyright 2025 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Integration with `git cl presubmit`.

See http://dev.chromium.org/developers/how-tos/depottools/presubmit-scripts for
details on the presubmit API built into `git cl`.
"""

from itertools import chain


PRESUBMIT_VERSION='2.0.0'

BACKWARDS_COMPAT_FOOTER = 'Breaking-Proto-Change-Ok'

_adjusted = [False]


def _adjustGlobalsOnce(input_api):
  if _adjusted[0]:
    return
  _adjusted[0] = True
  input_api.DEFAULT_FILES_TO_CHECK += (r'.+\.proto$',)
  input_api.DEFAULT_FILES_TO_SKIP += (r'.+_pb2\.pyi?$',)


def CheckLicense(input_api, output_api):
  _adjustGlobalsOnce(input_api)
  return input_api.canned_checks.CheckLicense(input_api, output_api)


def CheckProtoBackwardCompatibility(input_api, output_api):
  msg = output_api.PresubmitError
  to_add = []
  footers = input_api.change.GitFootersFromDescription()
  if reasons := footers.get(BACKWARDS_COMPAT_FOOTER):
    reason = '> ' + '\n> '.join(reasons)
    to_add.append(
        output_api.PresubmitPromptWarning(
            "Ignored `build.py breaking` result due to "
            f"{BACKWARDS_COMPAT_FOOTER} in CL description. Reason:"
            f"\n{reason}"))
    msg = output_api.PresubmitPromptWarning
  else:
    to_add.append(
        output_api.PresubmitError(
            "If this breaking change is expected, add the footer "
            f"`{BACKWARDS_COMPAT_FOOTER}: <your reason>` to the CL"
            " description."))

  rslt = input_api.RunTests([
      input_api.Command(
          name='build.py breaking',
          cmd=['build.py', 'breaking'],
          kwargs={'cwd': input_api.PresubmitLocalPath()},
          message=msg,
      )
  ])
  if any(r.fatal for r in rslt):
    rslt.extend(to_add)
  return rslt


def CheckAllTests(input_api, output_api):
  """This collects and runs all functions prefixed with test_.

    This is done because presubmit does not currently run top-level CheckXXX
    functions in parallel for some reason.

    Each `test_` function in this file is meant to return an iterable of
    input_api.Command objects.
    """
  return input_api.RunTests(
      chain.from_iterable(
          testFn(input_api, output_api)
          for name, testFn in globals().items()
          if name.startswith('test_')))


def test_Lint(input_api, output_api):
  return [
      input_api.Command(
          name='build.py lint',
          cmd=['build.py', 'lint'],
          kwargs={'cwd': input_api.PresubmitLocalPath()},
          message=output_api.PresubmitError,
      )
  ]


def test_Protoc(input_api, output_api):
  return [
      input_api.Command(
          name='build.py compile_desc',
          cmd=['build.py', 'compile_desc'],
          kwargs={'cwd': input_api.PresubmitLocalPath()},
          message=output_api.PresubmitError,
      )
  ]


def test_GoPackageOption(input_api, output_api):
  return [
      input_api.Command(
          name='build.py check_go_package',
          cmd=['build.py', 'check_go_package'],
          kwargs={'cwd': input_api.PresubmitLocalPath()},
          message=output_api.PresubmitError,
      )
  ]


def test_ServiceDefinitions(input_api, output_api):
  return [
      input_api.Command(
          name='build.py check_service_definitions',
          cmd=['build.py', 'check_service_definitions'],
          kwargs={'cwd': input_api.PresubmitLocalPath()},
          message=output_api.PresubmitError,
      )
  ]


def test_AllFieldsOptional(input_api, output_api):
  return [
      input_api.Command(
          name='build.py check_all_fields_optional',
          cmd=['build.py', 'check_all_fields_optional'],
          kwargs={'cwd': input_api.PresubmitLocalPath()},
          message=output_api.PresubmitError,
      )
  ]


def test_Stubs(input_api, output_api):
  return [
      input_api.Command(
          name='build.py compile_stubs check',
          cmd=['build.py', 'compile_stubs', 'check'],
          kwargs={'cwd': input_api.PresubmitLocalPath()},
          message=output_api.PresubmitError,
      )
  ]


def test_StoredDescriptors(input_api, output_api):
  return [
      input_api.Command(
          name='build.py store_descriptors check',
          cmd=['build.py', 'store_descriptors', 'check'],
          kwargs={'cwd': input_api.PresubmitLocalPath()},
          message=output_api.PresubmitError,
      )
  ]


def test_ProtoFormat(input_api, output_api):
  return [
      input_api.Command(
          name='build.py format check',
          cmd=['build.py', 'format', 'check'],
          kwargs={'cwd': input_api.PresubmitLocalPath()},
          message=output_api.PresubmitError,
      )
  ]


def test_PyFormat(input_api, output_api):
  _adjustGlobalsOnce(input_api)
  # Note: GetPylint returns a list of Command.
  return input_api.canned_checks.GetPylint(
      input_api,
      output_api,
      version='3.2',
      pylintrc='.pylintrc',
  )


def test_PyTests(input_api, output_api):
  return [
      input_api.Command(
          name='build.py test_python',
          cmd=['build.py', 'test_python', '-v'],
          kwargs={'cwd': input_api.PresubmitLocalPath()},
          message=output_api.PresubmitError,
      )
  ]
