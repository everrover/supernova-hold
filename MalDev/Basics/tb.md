### Throritical points:

L = long, P = ptr, C = constant, H = handle
A = ansi(char-set), W = wide(unicode) => CreateFileA, 

https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew

https://learn.microsoft.com/en-us/windows/win32/debug/system-error-codes--0-499-
https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-erref/596a1078-e883-4972-9bbc-49e60bebca55

### PE str
### ASLR mods the address space

DLLs, headers and usage - ~ to JS loads or Java module loads

**Signature based detection**
- Hash based sig detection
**Heuristic - mannual**
- Sandbox
- Static
**Behaviour**
- API hooking
- IAT checks

Windows processes, threads and memory
M/M => private, mapped, image

Process Env Block - PEB
- BeingDebugged - 0/1
- ProcessParams - cmd line params
- Ldr - DLL attachments
- AtlThunkSListPtr - Active Template Library - LL of `thunking functions` - fns in diff addr space
- PostProcessInitRoutine
- SessionId

Thread Env Block - TEB
- PEB ptr
- TlsSlots - Thread local stoage
- TlsExpansionSlots - for .dll's

APIs - OpenProcess/OpenThread/CloseHandle

Undocumented components and APIs
https://github.com/winsiderss/systeminformer/tree/master/phnt/include
https://web.archive.org/web/20230401045934/http://undocumented.ntinternals.net/
https://doxygen.reactos.org/globals_type.html
https://www.vergiliusproject.com/

Payload placement
.data - global & static var's - r/w allowed
.rsrc
.text - code section - r-x - allowed to execute directly without editing m/m permissions
.rdata - const var's - r-only

### Malware hiding techniques

- Payload encryption - [LINK](./enc_payloads.md)
  - Instead of storing the payload in clear text, it is encrypted and decrypted at runtime, whenever needed.
    - Chances of detection are reduced as the payload is not stored in a readable format, since code scans are rarely performed on memory since it is resource-intensive.
  - This can be done using symmetric or asymmetric encryption algorithms.
    - XOR encryption
    - RC4 enc, etc
    - AES, RSA, etc.
- Code/Payload obfuscation
  - IP Addr obfuscation
  - MAC obfuscation
  - UUID obfuscation
    - `801B18F0-8320-4ADA-BB13-41EA1C886B87` => `time-low - time-mid - time-high-and-version - clock-seq-and-reserved - node`
  - String obfuscation - e.g. skipping alternate characters
  - Binary-tree/Tree based - Basically some arbitary serializable/de-serializable data structure is used to store the payload, which is then traversed to get the actual payload.
- Code injection
- Being more specific
  - Using specific APIs or system calls that are less commonly used, making it harder for signature-based detection systems to identify the malware.
  - Using those application sections in arch specific assembly code that are less commonly used / monitored
