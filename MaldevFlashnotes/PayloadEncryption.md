# Payload encryption ^ obfuscation

Using algorithms such as RC4, XOR, AES, etc. payloads can be stored within m/m or storage. Only when they are needed they can be pulled within executable memory to be used.

Obfuscation can also help in this case. Examples: using some data-structures, or some other way. Ex - IPv4/IPv6 address lists/UUID/Addresses/DFS-path-and-graph/etc.

Reduces footprint and prevents the app being flagged during static/dynamic analysis.

```cpp

```