# vim: ft=python

use_relative_paths = True
git_dependencies = 'SUBMODULES'

deps = {
  'tools': {
    'packages': [
      {
        'package': 'infra/3pp/tools/protoc/${{os}}-${{arch=amd64,arm64}}',
        'version': 'version:3@32.1',
      },
    ],
    'dep_type': 'cipd',
  },
  'tools/bin': {
    'packages': [
      {
        'package': 'infra/3pp/go/github.com/bufbuild/buf/${{platform}}',
        'version': 'version:3@1.57.0',
      },
      {
        'package': 'infra/3pp/go/github.com/protocolbuffers/protoc-gen-go/${{platform}}',
        'version': 'version:3@1.36.9.chromium.1',
      },
      {
        'package': 'infra/3pp/go/github.com/grpc/protoc-gen-go-grpc/${{platform}}',
        'version': 'version:3@1.75.1.chromium.2',
      }
    ],
    'dep_type': 'cipd',
  }
}
