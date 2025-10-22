### DLL injection

Simply, a C++ concept, loading link-libs at runtime.

```cpp
// Link-lib code
#include <Windows.h>
#include <stdio.h>

VOID MsgBoxPayload() {
    MessageBoxA(NULL, "Hacking With MaldevAcademy", "Wow !", MB_OK | MB_ICONINFORMATION);
}


BOOL APIENTRY DllMain (HMODULE hModule, DWORD dwReason, LPVOID lpReserved){

    switch (dwReason){
        case DLL_PROCESS_ATTACH: {
            MsgBoxPayload();
            break;
        };
        case DLL_THREAD_ATTACH:
        case DLL_THREAD_DETACH:
        case DLL_PROCESS_DETACH:
            break;
    }

    return TRUE;
}

// Main method
#include <Windows.h>
#include <iostream>
#include <string>

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "[!] Missing Argument; Dll Payload To Run\n";
        return -1;
    }

    std::string dll = argv[1];
    std::cout << "[i] Injecting \"" << dll << "\" To The Local Process Of Pid: "
              << GetCurrentProcessId() << '\n';

    std::cout << "[+] Loading Dll... ";
    HMODULE h = LoadLibraryA(dll.c_str());
    if (!h) {
        std::cerr << "[!] LoadLibraryA Failed With Error : " << GetLastError() << '\n';
        return -1;
    }
    std::cout << "[+] DONE !\n";

    std::cout << "[#] Press <Enter> To Quit ... ";
    std::cin.get();

    return 0;
}

```