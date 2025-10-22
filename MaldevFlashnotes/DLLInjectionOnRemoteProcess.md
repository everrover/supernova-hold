## DLL-injection on a remote process

### Process enumeration [@LINK](./EnumerationProcess.md)

Simply, a C++ concept, loading link-libs at runtime in remote process.

The DLL loading function is placed on a thread and executed via `CreateRemoteThread` within the remote process.

```cpp
// Main method

#include <windows.h>
#include <string>
#include <iostream>

bool InjectDllToRemoteProcess(HANDLE hProcess, const std::wstring& dllName) {
    if (hProcess == NULL || hProcess == INVALID_HANDLE_VALUE) {
        std::wcerr << L"[!] Invalid process handle.\n";
        return false;
    }

    bool bState = true;
    LPVOID pLoadLibraryW = nullptr;
    LPVOID pAddress = nullptr;
    SIZE_T bytesWritten = 0;
    HANDLE hThread = nullptr;

    // include null terminator
    SIZE_T dwSizeToWrite = (dllName.length() + 1) * sizeof(wchar_t);

    // resolve LoadLibraryW
    pLoadLibraryW = reinterpret_cast<LPVOID>(
        GetProcAddress(GetModuleHandleW(L"kernel32.dll"), "LoadLibraryW")
    );
    if (pLoadLibraryW == nullptr) {
        std::wcerr << L"[!] GetProcAddress failed with error: " << GetLastError() << L"\n";
        return false;
    }

    // allocate memory in remote process
    pAddress = VirtualAllocEx(hProcess, nullptr, dwSizeToWrite, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    if (pAddress == nullptr) {
        std::wcerr << L"[!] VirtualAllocEx failed with error: " << GetLastError() << L"\n";
        return false;
    }

    std::wcout << L"[i] pAddress allocated at: " << pAddress << L" size: " << dwSizeToWrite << L" bytes\n";

    // write the DLL path to the remote process memory
    if (!WriteProcessMemory(hProcess, pAddress, dllName.c_str(), dwSizeToWrite, &bytesWritten) || bytesWritten != dwSizeToWrite) {
        std::wcerr << L"[!] WriteProcessMemory failed with error: " << GetLastError() << L"\n";
        // free remote memory
        VirtualFreeEx(hProcess, pAddress, 0, MEM_RELEASE);
        return false;
    }

    std::wcout << L"[i] Successfully written " << bytesWritten << L" bytes\n";

    // create remote thread to call LoadLibraryW
    hThread = CreateRemoteThread(
        hProcess,
        nullptr,
        0,
        reinterpret_cast<LPTHREAD_START_ROUTINE>(pLoadLibraryW),
        pAddress,
        0,
        nullptr
    );

    if (hThread == nullptr) {
        std::wcerr << L"[!] CreateRemoteThread failed with error: " << GetLastError() << L"\n";
        VirtualFreeEx(hProcess, pAddress, 0, MEM_RELEASE);
        return false;
    }

    // RAII: ensure handle closed
    auto threadCloser = [](HANDLE h) { if (h) CloseHandle(h); };
    std::unique_ptr<void, decltype(threadCloser)> threadGuard(hThread, threadCloser);

    std::wcout << L"[i] Remote thread created, waiting for it to finish...\n";

    // optionally wait for the thread to finish (waits 10 seconds here, change as needed)
    DWORD waitRes = WaitForSingleObject(hThread, 10000);
    if (waitRes == WAIT_FAILED) {
        std::wcerr << L"[!] WaitForSingleObject failed with error: " << GetLastError() << L"\n";
        bState = false;
    } else if (waitRes == WAIT_TIMEOUT) {
        std::wcout << L"[i] Remote thread did not finish within timeout (10s). Continuing.\n";
        // not necessarily an error; the DLL may still be loading.
    } else {
        std::wcout << L"[+] Remote thread finished.\n";
    }

    // free the injected string memory in the remote process
    if (!VirtualFreeEx(hProcess, pAddress, 0, MEM_RELEASE)) {
        std::wcerr << L"[!] VirtualFreeEx failed with error: " << GetLastError() << L"\n";
        // not a fatal error for the injection itself
    }

    return bState;
}

// process enum code ...

int main(int argc, char* argv[]) {
	// PrintProcesses();
	DWORD pdwPid;
	HANDLE phProcess;
	LPCWSTR pname = L"atom.exe";
	GetRemoteProcessHandle(pname, &pdwPid, &phProcess );
    
    std::string dll = argv[1];
    InjectDllToRemoteProcess(phProcess, "ntdll.dll");
    std::cin.get();

    return 0;
}

```