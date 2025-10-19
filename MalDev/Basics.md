# Payload placement

Learnt how processes are created and how memory is allocated, we can now look at how to place our payload in memory.

- Windows
  - .data & .rdata sections
  - Heap
  - Stack
  - .text section
  - .rsrc section
- Payload encryption
  - XOR
  - AES
  - RC4
  - Custom algorithms : Base64, Base85, etc.
- Payload encoding/Obfuscation
  - Shikata Ga Nai
  - Alpha2/3
  - Custom encoders
  - IPv4/IPv6
  - MACfuscation - Using MAC addresses to encode payloads
  - UUID/GUID - Using UUIDs/GUIDs to encode payloads
  - Custom serializers and deserializers using JSON, XML, YAML, etc. or data structures like linked lists, trees, graphs, etc.

I built a tool for performing payload encoding/obfuscation/encryption called [Necromancer](./Necromancer/Necromancer.md).

## Shellcode injection within processes

- 