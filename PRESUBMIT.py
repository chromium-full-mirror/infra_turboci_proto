# Copyright 2025 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Integration with `git cl presubmit`.

See http://dev.chromium.org/developers/how-tos/depottools/presubmit-scripts for
details on the presubmit API built into `git cl`.
"""

PRESUBMIT_VERSION='2.0.0'

BACKWARDS_COMPAT_FOOTER = 'Breaking-Proto-Change-Ok'


def CheckProtoBackwardCompatibility(input_api, output_api):
  msg = output_api.PresubmitError
  to_add = []
  footers = input_api.change.GitFootersFromDescription()
  if reasons := footers.get(BACKWARDS_COMPAT_FOOTER):
    reason = '> ' + '\n> '.join(reasons)
    to_add.append(output_api.PresubmitPromptWarning(
        "Ignored `build.py breaking` result due to "
        f"{BACKWARDS_COMPAT_FOOTER} in CL description. Reason:\n{reason}"
    ))
    msg = output_api.PresubmitPromptWarning
  else:
    to_add.append(output_api.PresubmitError(
        "If this breaking change is expected, add the footer "
        f"`{BACKWARDS_COMPAT_FOOTER}: <your reason>` to the CL description."
    ))

  rslt = input_api.RunTests([input_api.Command(
      name='build.py breaking',
      cmd=['build.py', 'breaking'],
      kwargs={'cwd': input_api.PresubmitLocalPath()},
      message=msg,
  )])
  if any(r.fatal for r in rslt):
    rslt.extend(to_add)
  return rslt


def CheckLint(input_api, output_api):
  return input_api.RunTests([input_api.Command(
      name='build.py lint',
      cmd=['build.py', 'lint'],
      kwargs={'cwd': input_api.PresubmitLocalPath()},
      message=output_api.PresubmitError,
  )])


def CheckProtoc(input_api, output_api):
  return input_api.RunTests([input_api.Command(
      name='build.py compile_desc',
      cmd=['build.py', 'compile_desc'],
      kwargs={'cwd': input_api.PresubmitLocalPath()},
      message=output_api.PresubmitError,
  )])


def CheckOneDeclPerFile(input_api, output_api):
  return input_api.RunTests([input_api.Command(
      name='build.py check_one_per_file',
      cmd=['build.py', 'check_one_per_file'],
      kwargs={'cwd': input_api.PresubmitLocalPath()},
      message=output_api.PresubmitError,
  )])


def CheckLicense(input_api, output_api):
  input_api.DEFAULT_FILES_TO_CHECK += (r'.+\.proto$',)
  return input_api.canned_checks.CheckLicense(input_api, output_api)


def CheckGoStubs(input_api, output_api):
  return input_api.RunTests([input_api.Command(
      name='build.py compile_go check',
      cmd=['build.py', 'compile_go', 'check'],
      kwargs={'cwd': input_api.PresubmitLocalPath()},
      message=output_api.PresubmitError,
  )])


def CheckFormat(input_api, output_api):
  return input_api.RunTests([input_api.Command(
      name='build.py format check',
      cmd=['build.py', 'format', 'check'],
      kwargs={'cwd': input_api.PresubmitLocalPath()},
      message=output_api.PresubmitError,
  )])
