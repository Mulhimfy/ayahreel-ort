"""ONNX Runtime 1.31.1, minimal build: interop_api.cc defines the three
Release* functions of the interop API table only inside its
!ORT_MINIMAL_BUILD block (their bodies even carry the minimal-build
branch), so a minimal static library references them undefined and an
app that links it fails (iOS). Adds their minimal-build definitions
(nothing to free: a minimal build makes no importers or handles).
usage: python3 minimal_interop_release.py <onnxruntime checkout>"""
import pathlib
import sys

p = pathlib.Path(sys.argv[1]) / 'onnxruntime/core/session/interop_api.cc'
s = p.read_text()
mark = '#else  // defined(ORT_MINIMAL_BUILD)\n'
add = '''
ORT_API(void, OrtInteropAPI::ReleaseExternalResourceImporter, _Frees_ptr_opt_ OrtExternalResourceImporter* importer) {
  ORT_UNUSED_PARAMETER(importer);
}

ORT_API(void, OrtInteropAPI::ReleaseExternalMemoryHandle, _Frees_ptr_opt_ OrtExternalMemoryHandle* handle) {
  ORT_UNUSED_PARAMETER(handle);
}

ORT_API(void, OrtInteropAPI::ReleaseExternalSemaphoreHandle, _Frees_ptr_opt_ OrtExternalSemaphoreHandle* handle) {
  ORT_UNUSED_PARAMETER(handle);
}
'''
assert s.count(mark) == 1, 'layout changed: look at interop_api.cc'
minimal = s.split(mark)[1].split('#endif  // !defined(ORT_MINIMAL_BUILD)')[0]
if 'ORT_API(void, OrtInteropAPI::ReleaseExternalMemoryHandle' in minimal:
    print('already defined for minimal builds')
    sys.exit(0)
p.write_text(s.replace(mark, mark + add))
print('patched', p)
