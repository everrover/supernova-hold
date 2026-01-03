# Spoofing Process(and application) Arguments

Evasion technique. Allows concealing the real args to monitoring tools and defenders
- `powershell.exe -c calc.exe` will be picked up, wheareas `powershell.exe -c notepad.exe` may not

PEB Windows: RTL_USER_PROCESS_PARAMETERS holds the args as a List(pointer-to-pointer format) of Unicode strings.

### Method #1

!Overwritten payload within the args list must be smaller or equal to the original args length!

```cpp
// Create process with dummy args, in suspended state
ProcessBasicInformation pbi = {0};
NTSTATUS nts = NtQueryInformationProcess(targetProcessHandle, ProcessBasicInformation, &pbi, sizeof(pbi), NULL);
// Read PEB -> ProcessParameters

// Read and overwrite ProcessParameters.CommandLine.Buffer

// Resume process
```