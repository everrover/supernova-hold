

// XOR encryption
void XorByOneKey(IN PBYTE pShellCode, IN SIZE_T sShellCodeSize, IN BYTE bKey) {
    if (pShellCode == nullptr || pKey == nullptr || sShellCodeSize == 0 || sKeySize == 0) {
        return; // Invalid parameters
    }

    for (SIZE_T i = 0; i < sShellCodeSize; ++i) {
        pShellCode[i] ^= pKey[i % sKeySize];
    }
}