# Copyright 2025 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Integration with `git cl presubmit`.

See http://dev.chromium.org/developers/how-tos/depottools/presubmit-scripts for
details on the presubmit API built into `git cl`.
"""

PRESUBMIT_VERSION='2.0.0'

ALLOWED_PREFIXES = (
  'google.golang.org/',
  'golang.org/'
)


def CheckGoSumOnlyRequiresFirstParty(input_api, output_api):
  files = input_api.AffectedFiles(
      include_deletes=False,
      file_filter=lambda file: file.LocalPath() == 'go/go.mod')
  if not files:
    return []

  directly_required_packages: list[tuple[int, str]] = []

  in_group = False
  for i, line in enumerate(files[0].NewContents()):
    line: str
    line = line.strip()
    if not line or line.startswith('//'):
      continue
    if in_group:
      if line == ')':
        in_group = False
      elif not line.endswith('// indirect'):
        directly_required_packages.append((i, line.split()[0]))
    else:
      if line.startswith('require'):
        if line == 'require (':
          in_group = True
        elif not line.endswith('// indirect'):
          directly_required_packages.append((i, line.split()[1]))

  ret = []
  for linenum, pkg in directly_required_packages:
    if pkg.startswith(ALLOWED_PREFIXES):
      continue

    ret.append(output_api.PresubmitError(
        f'go.mod:{linenum+1} - bad requirement {pkg!r}'
    ))

  if ret:
    ret.append(output_api.PresubmitError(
        f'go.mod - only allowed to require packages in {ALLOWED_PREFIXES}.'
    ))

  return ret
