// ------------------------------------------------ ----------------------
bool VMwareDetect ()
{
__try
        {
        __asm
                {
                mov eax, 0x564d5868
                mov ecx, 0x0A
                mov edx, 0x5658
                in eax, dx
                }
        return true;
        }
__except (EXCEPTION_EXECUTE_HANDLER)
        {
        return false;
        }
}
// ------------------------------------------------ ----------------------
bool VirtualPCDetect ()
{
__try
        {
        __asm
                {
                xor ebx, ebx
                mov eax, 1
                __emit (0x0F)
                __emit (0x3F)
                __emit (0x07)
                __emit (0x0B)
                }
        return true;
        }
__except (EXCEPTION_EXECUTE_HANDLER)
        {
         return false;
        }
}
// ------------------------------------------------ ----------------------
bool VMwareWindowDetect ()
{
HWND VMwareWindow = NULL;
VMwareWindow = FindWindowA ( "VMSwitchUserControlClass", NULL);
if (VMwareWindow! = NULL)
        {
        return true;
        }
return false;
}
// ------------------------------------------------ ----------------------
bool VirtualBoxWindowDetect ()
{
HWND VBoxWindow = NULL;
VBoxWindow = FindWindowA ( "VBoxTrayToolWndClass", NULL);
if (VBoxWindow! = NULL)
        {
        return true;
        }
return false;
}
// ------------------------------------------------ ----------------------
bool VMwareBIOSDetect ()
{
HKEY rKey;
wchar_t RegKey [256];
wchar_t RegVMware [] = {L "VMware Virtual Platform"};
DWORD RegPath = sizeof (RegKey);
 
RegOpenKeyEx (HKEY_LOCAL_MACHINE,
                         L "HARDWARE \\ DESCRIPTION \\ System \\ BIOS",
                         0
                         KEY_QUERY_VALUE,
                         & Amp; rKey);
 
RegQueryValueEx (rKey,
                                L "SystemProductName",
                                NULL,
                                NULL,
                                (BYTE *) RegKey,
                                & Amp; RegPath);
 
RegCloseKey (rKey);
 
if (memcmp (RegKey, RegVMware, 48) == 0)
        {
        return true;
        }
return false;
}
// ------------------------------------------------ ----------------------
bool VirtualBoxBIOSDetect ()
{
HKEY rKey;
wchar_t RegKey [256];
wchar_t RegVBox [] = {L "Oracle VM VirtualBox"};
DWORD RegPath = sizeof (RegKey);
 
RegOpenKeyEx (HKEY_LOCAL_MACHINE,
                         L "HARDWARE \\ DESCRIPTION \\ System",
                         0
                         KEY_QUERY_VALUE,
                         & Amp; rKey);
 
RegQueryValueEx (rKey,
                                L "VideoBiosVersion",
                                NULL,
                                NULL,
                                (BYTE *) RegKey,
                                & Amp; RegPath);
 
RegCloseKey (rKey);
 
if (memcmp (RegKey, RegVBox, 40) == 0)
        {
        return true;
        }
return false;
}
// ------------------------------------------------ ----------------------
bool ParallelsRegDetect ()
{
HKEY rKey;
 
if (RegOpenKeyEx (HKEY_LOCAL_MACHINE,
                                L "HARDWARE \\ ACPI \\ DSDT \\ PRLS __ \\ PRLSACPI",
                                0
                                KEY_QUERY_VALUE,
                                & Amp; rKey) == ERROR_SUCCESS)
        {
        RegCloseKey (rKey);
        return true;
        }
return false;
}
// ------------------------------------------------ ----------------------
bool VirtualBoxProcessDetect ()
{
wchar_t VBoxProcessName [] = {L "VBoxTray.exe"};
PROCESSENTRY32 pe;
HANDLE hSnapShot;
hSnapShot = CreateToolhelp32Snapshot (TH32CS_SNAPPROCESS, 0);
ZeroMemory (& amp; pe, sizeof (PROCESSENTRY32W));
pe.dwSize = sizeof (PROCESSENTRY32W);
Process32First (hSnapShot, & amp; pe);
do
{
if (memcmp (pe.szExeFile, VBoxProcessName, 24) == 0)
        {
         CloseHandle (hSnapShot);
         return true;
        }
}
while (Process32Next (hSnapShot, & amp; pe));
CloseHandle (hSnapShot);
return false;
}
// ------------------------------------------------ ----------------------
bool VirtualPCProcessDetect ()
{
wchar_t VirtualPCProcessName [] = {L "vmusrvc.exe"};
PROCESSENTRY32 pe;
HANDLE hSnapShot;
hSnapShot = CreateToolhelp32Snapshot (TH32CS_SNAPPROCESS, 0);
ZeroMemory (& amp; pe, sizeof (PROCESSENTRY32W));
pe.dwSize = sizeof (PROCESSENTRY32W);
Process32First (hSnapShot, & amp; pe);
do
{
if (memcmp (pe.szExeFile, VirtualPCProcessName, 22) == 0)
        {
         CloseHandle (hSnapShot);
         return true;
        }
}
while (Process32Next (hSnapShot, & amp; pe));
CloseHandle (hSnapShot);
return false;
}
// ------------------------------------------------ ----------------------
bool VMwareProcessDetect ()
{
wchar_t VMwareProcessName [] = {L "vmtoolsd.exe"};
PROCESSENTRY32 pe;
HANDLE hSnapShot;
hSnapShot = CreateToolhelp32Snapshot (TH32CS_SNAPPROCESS, 0);
ZeroMemory (& amp; pe, sizeof (PROCESSENTRY32W));
pe.dwSize = sizeof (PROCESSENTRY32W);
Process32First (hSnapShot, & amp; pe);
do
{
if (memcmp (pe.szExeFile, VMwareProcessName, 24) == 0)
        {
         CloseHandle (hSnapShot);
         return true;
        }
}
while (Process32Next (hSnapShot, & amp; pe));
CloseHandle (hSnapShot);
return false;
}
// ------------------------------------------------ ----------------------
bool VirtualBoxDevObjDetect ()
{
if ((CreateFile (L "\\\\. \\ VBoxMiniRdrDN", 0,0,0, OPEN_EXISTING, 0,0)! =
        INVALID_HANDLE_VALUE) ||
        (CreateFile (L "\\\\. \\ VBoxGuest", 0,0,0, OPEN_EXISTING, 0,0)! =
        INVALID_HANDLE_VALUE))
        {
        return true;
        }
else
        {
        return false;
        }
}
// ------------------------------------------------ ----------------------
bool VirtualPCDevObjDetect ()
{
if (CreateFile (L "\\\\. \\ VMDRV", 0,0,0, OPEN_EXISTING, 0,0)! =
        INVALID_HANDLE_VALUE)
        {
        return true;
        }
else
        {
        return false;
        }
}
// ------------------------------------------------ ----------------------
bool VirtualBoxCPUIDDetect ()
{
DWORD ID_1, ID_2, ID_3;
_asm
        {
        mov eax, 0x1
        cpuid
        mov eax, 0x40000000
        cpuid
        mov ID_1, ebx
        mov ID_2, ecx
        mov ID_3, edx
        }
if ((ID_1 == 0x00000340) & amp; & amp; (ID_2 == 0x00000340))
        {
        return true;
        }
else
        {
        return false;
        }
}
// ------------------------------------------------ ----------------------
bool VMwareCPUIDDetect ()
{
DWORD ID_1, ID_2, ID_3;
_asm
        {
        mov eax, 0x1
        cpuid
        mov eax, 0x40000000
        cpuid
        mov ID_1, ebx
        mov ID_2, ecx
        mov ID_3, edx
        }
if ((ID_1 == 0x61774d56) & amp; & amp; (ID_2 == 0x4d566572) & amp; & amp; (ID_3 == 0x65726177))
        {
        return true;
        }
else
        {
        return false;
        }
}
// ------------------------------------------------ ----------------------
bool ParallelsCPUIDDetect ()
{
DWORD ID_1, ID_2, ID_3;
_asm
        {
        mov eax, 0x1
        cpuid
        mov eax, 0x40000000
        cpuid
        mov ID_1, ebx
        mov ID_2, ecx
        mov ID_3, edx
        }
if ((ID_1 == 0x70726c20) & amp; & amp; (ID_2 == 0x68797065) & amp; & amp; (ID_3 == 0x72762020))
        {
        return true;
        }
else
        {
        return false;
        }
}
// ------------------------------------------------ ----------------------
bool VirtualPCMACDetect ()
{
PIP_ADAPTER_INFO AdapterInfo = NULL;
DWORD OutBufLen;
GetAdaptersInfo (AdapterInfo, & amp; OutBufLen);
AdapterInfo = (PIP_ADAPTER_INFO) new (char [OutBufLen]);
GetAdaptersInfo (AdapterInfo, & amp; OutBufLen);
if (((BYTE) AdapterInfo- & gt; Address [0] == 0x00) & amp; & amp;
        ((BYTE) AdapterInfo- & gt; Address [1] == 0x03) & amp; & amp;
        ((BYTE) AdapterInfo- & gt; Address [2] == 0xff) ||
        ((BYTE) AdapterInfo- & gt; Address [0] == 0x00) & amp; & amp;
        ((BYTE) AdapterInfo- & gt; Address [1] == 0x12) & amp; & amp;
        ((BYTE) AdapterInfo- & gt; Address [2] == 0x5a) ||
        ((BYTE) AdapterInfo- & gt; Address [0] == 0x00) & amp; & amp;
        ((BYTE) AdapterInfo- & gt; Address [1] == 0x1d) & amp; & amp;
        ((BYTE) AdapterInfo- & gt; Address [2] == 0xd8) ||
        ((BYTE) AdapterInfo- & gt; Address [0] == 0x00) & amp; & amp;
        ((BYTE) AdapterInfo- & gt; Address [1] == 0x15) & amp; & amp;
        ((BYTE) AdapterInfo- & gt; Address [2] == 0x5d) ||
        ((BYTE) AdapterInfo- & gt; Address [0] == 0x00) & amp; & amp;
        ((BYTE) AdapterInfo- & gt; Address [1] == 0x22) & amp; & amp;
        ((BYTE) AdapterInfo- & gt; Address [2] == 0x48) ||
        ((BYTE) AdapterInfo- & gt; Address [0] == 0x00) & amp; & amp;
        ((BYTE) AdapterInfo- & gt; Address [1] == 0x0d) & amp; & amp;
        ((BYTE) AdapterInfo- & gt; Address [2] == 0x3a) ||
        ((BYTE) AdapterInfo- & gt; Address [0] == 0x00) & amp; & amp;
        ((BYTE) AdapterInfo- & gt; Address [1] == 0x17) & amp; & amp;
        ((BYTE) AdapterInfo- & gt; Address [2] == 0xfa) ||
        ((BYTE) AdapterInfo- & gt; Address [0] == 0x00) & amp; & amp;
        ((BYTE) AdapterInfo- & gt; Address [1] == 0x25) & amp; & amp;
        ((BYTE) AdapterInfo- & gt; Address [2] == 0xae) ||
        ((BYTE) AdapterInfo- & gt; Address [0] == 0x00) & amp; & amp;
        ((BYTE) AdapterInfo- & gt; Address [1] == 0x50) & amp; & amp;
        ((BYTE) AdapterInfo- & gt; Address [2] == 0xf2) ||
        ((BYTE) AdapterInfo- & gt; Address [0] == 0x28) & amp; & amp;
        ((BYTE) AdapterInfo- & gt; Address [1] == 0x18) & amp; & amp;
        ((BYTE) AdapterInfo- & gt; Address [2] == 0x78) ||
        ((BYTE) AdapterInfo- & gt; Address [0] == 0x60) & amp; & amp;
        ((BYTE) AdapterInfo- & gt; Address [1] == 0x45) & amp; & amp;
        ((BYTE) AdapterInfo- & gt; Address [2] == 0xbd) ||
        ((BYTE) AdapterInfo- & gt; Address [0] == 0x7c) & amp; & amp;
        ((BYTE) AdapterInfo- & gt; Address [1] == 0x1e) & amp; & amp;
        ((BYTE) AdapterInfo- & gt; Address [2] == 0x52) ||
        ((BYTE) AdapterInfo- & gt; Address [0] == 0x7c) & amp; & amp;
        ((BYTE) AdapterInfo- & gt; Address [1] == 0xed) & amp; & amp;
        ((BYTE) AdapterInfo- & gt; Address [2] == 0x8d) ||
        ((BYTE) AdapterInfo- & gt; Address [0] == 0xdc) & amp; & amp;
        ((BYTE) AdapterInfo- & gt; Address [1] == 0xb4) & amp; & amp;
        ((BYTE) AdapterInfo- & gt; Address [2] == 0xc4))
        {
        delete (AdapterInfo);
        return true;
        }
else
        {
        delete (AdapterInfo);
        return false;
        }
}
// ------------------------------------------------ ----------------------
bool VirtualBoxMACDetect ()
{
PIP_ADAPTER_INFO AdapterInfo = NULL;
DWORD OutBufLen;
GetAdaptersInfo (AdapterInfo, & amp; OutBufLen);
AdapterInfo = (PIP_ADAPTER_INFO) new (char [OutBufLen]);
GetAdaptersInfo (AdapterInfo, & amp; OutBufLen);
if (((BYTE) AdapterInfo- & gt; Address [0] == 0x08) & amp; & amp;
        ((BYTE) AdapterInfo- & gt; Address [1] == 0x00) & amp; & amp;
        ((BYTE) AdapterInfo- & gt; Address [2] == 0x27) ||
        ((BYTE) AdapterInfo- & gt; Address [0] == 0x08) & amp; & amp;
        ((BYTE) AdapterInfo- & gt; Address [1] == 0x00) & amp; & amp;
        ((BYTE) AdapterInfo- & gt; Address [2] == 0x20))
        {
        delete (AdapterInfo);
        return true;
        }
else
        {
        delete (AdapterInfo);
        return false;
        }
}
// ------------------------------------------------ ----------------------
 
bool VMwareMACDetect ()
{
PIP_ADAPTER_INFO AdapterInfo = NULL;
DWORD OutBufLen;
GetAdaptersInfo (AdapterInfo, & amp; OutBufLen);
AdapterInfo = (PIP_ADAPTER_INFO) new (char [OutBufLen]);
GetAdaptersInfo (AdapterInfo, & amp; OutBufLen);
if (((BYTE) AdapterInfo- & gt; Address [0] == 0x00) & amp; & amp;
        ((BYTE) AdapterInfo- & gt; Address [1] == 0x05) & amp; & amp;
        ((BYTE) AdapterInfo- & gt; Address [2] == 0x69) ||
        ((BYTE) AdapterInfo- & gt; Address [0] == 0x00) & amp; & amp;
        ((BYTE) AdapterInfo- & gt; Address [1] == 0x0c) & amp; & amp;
        ((BYTE) AdapterInfo- & gt; Address [2] == 0x29) ||
        ((BYTE) AdapterInfo- & gt; Address [0] == 0x00) & amp; & amp;
        ((BYTE) AdapterInfo- & gt; Address [1] == 0x1c) & amp; & amp;
        ((BYTE) AdapterInfo- & gt; Address [2] == 0x14) ||
        ((BYTE) AdapterInfo- & gt; Address [0] == 0x00) & amp; & amp;
        ((BYTE) AdapterInfo- & gt; Address [1] == 0x50) & amp; & amp;
        ((BYTE) AdapterInfo- & gt; Address [2] == 0x56))
        {
        delete (AdapterInfo);
        return true;
        }
else
        {
        delete (AdapterInfo);
        return false;
        }
}
// ------------------------------------------------ ----------------------
bool ParallelsMACDetect ()
{
PIP_ADAPTER_INFO AdapterInfo = NULL;
DWORD OutBufLen;
GetAdaptersInfo (AdapterInfo, & amp; OutBufLen);
AdapterInfo = (PIP_ADAPTER_INFO) new (char [OutBufLen]);
GetAdaptersInfo (AdapterInfo, & amp; OutBufLen);
if (((BYTE) AdapterInfo- & gt; Address [0] == 0x00) & amp; & amp;
        ((BYTE) AdapterInfo- & gt; Address [1] == 0x1c) & amp; & amp;
        ((BYTE) AdapterInfo- & gt; Address [2] == 0x42))
        {
        delete (AdapterInfo);
        return true;
        }
else
        {
        delete (AdapterInfo);
        return false;
        }
}
// ------------------------------------------------ ----------------------
bool VirtualMachineIDDiskDetect (char * IDDisk)
{
HKEY rKey;
char RegKey [4096];
DWORD RegPath = sizeof (RegKey);
DWORD Type = REG_SZ;
 
RegOpenKeyExA (HKEY_LOCAL_MACHINE,
                         "SYSTEM \\ CurrentControlSet \\ Services \\ Disk \\ Enum",
                         0
                         KEY_QUERY_VALUE,
                         & Amp; rKey);
 
RegQueryValueExA (rKey,
                                "0"
                                NULL,
                                & Amp; Type,
                                (LPBYTE) RegKey,
                                & Amp; RegPath);
 
RegCloseKey (rKey);
 
if (strstr (RegKey, IDDisk)! = 0)
        {
        return true;
        }
return false;
}
// ------------------------------------------------ ----------------------
bool ParallelsVideoCardDetect ()
{
HKEY rKey;
 
if (RegOpenKeyEx (HKEY_LOCAL_MACHINE,
                                L "SYSTEM \\ CurrentControlSet \\ Enum \\ PCI \\ VEN_1AB8 & amp; DEV_4005 & amp; SUBSYS_04001AB8 & amp; REV_00",
                                0
                                KEY_QUERY_VALUE,
                                & Amp; rKey) == ERROR_SUCCESS)
        {
        RegCloseKey (rKey);
        return true;
        }
return false;
}
// ------------------------------------------------ ----------------------
bool VirtualBoxVideoCardDetect ()
{
HKEY rKey;
 
if (RegOpenKeyEx (HKEY_LOCAL_MACHINE,
                                L "SYSTEM \\ CurrentControlSet \\ Enum \\ PCI \\ VEN_80EE & amp; DEV_BEEF & amp; SUBSYS_00000000 & amp; REV_00",
                                0
                                KEY_QUERY_VALUE,
                                & Amp; rKey) == ERROR_SUCCESS)
        {
        RegCloseKey (rKey);
        return true;
        }
return false;
}
// ------------------------------------------------ ----------------------
bool VirtualPCVideoCardDetect ()
{
HKEY rKey;
 
if (RegOpenKeyEx (HKEY_LOCAL_MACHINE,
                                L "SYSTEM \\ CurrentControlSet \\ Enum \\ PCI \\ VEN_5333 & amp; DEV_8811 & amp; SUBSYS_00000000 & amp; REV_00",
                                0
                                KEY_QUERY_VALUE,
                                & Amp; rKey) == ERROR_SUCCESS)
        {
        RegCloseKey (rKey);
        return true;
        }
return false;
}
// ------------------------------------------------ ----------------------
