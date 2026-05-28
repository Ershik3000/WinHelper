#include <windows.h>
#include <string>
#include <sstream>
#include <psapi.h>
#include <tlhelp32.h>
#include <lm.h>

#pragma comment(lib, "psapi.lib")
#pragma comment(lib, "netapi32.lib")

std::string escape_json(const std::string& s) {
    std::string escaped;
    for (char c : s) {
        switch (c) {
            case '"': escaped += "\\\""; break;
            case '\\': escaped += "\\\\"; break;
            case '\n': escaped += "\\n"; break;
            case '\r': escaped += "\\r"; break;
            case '\t': escaped += "\\t"; break;
            default: escaped += c;
        }
    }
    return escaped;
}

std::string wchar_to_string(WCHAR* wstr) {
    if (!wstr) return "";
    char buffer[512];
    WideCharToMultiByte(CP_UTF8, 0, wstr, -1, buffer, sizeof(buffer), NULL, NULL);
    return std::string(buffer);
}

void GetRunEntries(HKEY hBase, const char* path, const char* sectionName, std::stringstream& json, BOOL& first) {
    HKEY hKey;
    LONG result = RegOpenKeyExA(hBase, path, 0, KEY_READ, &hKey);
    if (result == ERROR_SUCCESS) {
        for (int i = 0; ; i++) {
            char name[256];
            char data[1024];
            DWORD nameSize = sizeof(name);
            DWORD dataSize = sizeof(data);
            
            if (RegEnumValueA(hKey, i, name, &nameSize, NULL, NULL, 
                            (LPBYTE)data, &dataSize) != ERROR_SUCCESS) break;
            
            if (!first) json << ",";
            first = FALSE;
            
            json << "{\"section\":\"" << sectionName 
                 << "\",\"name\":\"" << escape_json(name) 
                 << "\",\"path\":\"" << escape_json(data) 
                 << "\",\"enabled\":true}";
        }
        RegCloseKey(hKey);
    }
}

extern "C" {
    __declspec(dllexport) char* GetStartupEntries() {
        std::stringstream json;
        json << "[";
        BOOL first = TRUE;
        
        HKEY hKey;
        
        if (RegOpenKeyExA(HKEY_LOCAL_MACHINE,
            "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon",
            0, KEY_READ, &hKey) == ERROR_SUCCESS) {
            
            char value[512];
            DWORD size = sizeof(value);
            
            if (RegQueryValueExA(hKey, "Shell", NULL, NULL, (LPBYTE)value, &size) == ERROR_SUCCESS) {
                if (!first) json << ",";
                first = FALSE;
                json << "{\"section\":\"Winlogon\",\"name\":\"Shell\",\"path\":\"" 
                     << escape_json(value) << "\",\"enabled\":true}";
            }
            
            size = sizeof(value);
            if (RegQueryValueExA(hKey, "Userinit", NULL, NULL, (LPBYTE)value, &size) == ERROR_SUCCESS) {
                if (!first) json << ",";
                first = FALSE;
                json << "{\"section\":\"Winlogon\",\"name\":\"Userinit\",\"path\":\"" 
                     << escape_json(value) << "\",\"enabled\":true}";
            }

            size = sizeof(value);
            if (RegQueryValueExA(hKey, "Taskman", NULL, NULL, (LPBYTE)value, &size) == ERROR_SUCCESS) {
                if (!first) json << ",";
                first = FALSE;
                json << "{\"section\":\"Winlogon\",\"name\":\"Taskman\",\"path\":\"" 
                     << escape_json(value) << "\",\"enabled\":true}";
            }
            RegCloseKey(hKey);
        }
        
        if (RegOpenKeyExA(HKEY_LOCAL_MACHINE,
            "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Windows",
            0, KEY_READ, &hKey) == ERROR_SUCCESS) {
            
            char value[512];
            DWORD size = sizeof(value);
            
            if (RegQueryValueExA(hKey, "AppInit_DLLs", NULL, NULL, (LPBYTE)value, &size) == ERROR_SUCCESS) {
                if (!first) json << ",";
                first = FALSE;
                json << "{\"section\":\"AppInit\",\"name\":\"AppInit_DLLs\",\"path\":\"" 
                     << escape_json(value) << "\",\"enabled\":true}";
            }

            size = sizeof(value);
            if (RegQueryValueExA(hKey, "LoadAppInit_DLLs", NULL, NULL, (LPBYTE)value, &size) == ERROR_SUCCESS) {
                if (!first) json << ",";
                first = FALSE;
                json << "{\"section\":\"AppInit\",\"name\":\"LoadAppInit_DLLs\",\"path\":\"" 
                     << escape_json(value) << "\",\"enabled\":true}";
            }
            RegCloseKey(hKey);
        }
        
        GetRunEntries(HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run", "Run", json, first);
        GetRunEntries(HKEY_CURRENT_USER, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run", "Run", json, first);
        GetRunEntries(HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\RunOnce", "RunOnce", json, first);
        GetRunEntries(HKEY_CURRENT_USER, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\RunOnce", "RunOnce", json, first);
        GetRunEntries(HKEY_LOCAL_MACHINE, "SOFTWARE\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Run", "Run", json, first);
        GetRunEntries(HKEY_CURRENT_USER, "SOFTWARE\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Run", "Run", json, first);
        
        GetRunEntries(HKEY_LOCAL_MACHINE, 
            "SOFTWARE\\Microsoft\\Internet Explorer\\Extensions", "IE", json, first);
        GetRunEntries(HKEY_CURRENT_USER, 
            "SOFTWARE\\Microsoft\\Internet Explorer\\Extensions", "IE", json, first);
        
        GetRunEntries(HKEY_LOCAL_MACHINE, 
            "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\ShellServiceObjects", "ShellExt", json, first);
        GetRunEntries(HKEY_LOCAL_MACHINE, 
            "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Browser Helper Objects", "BHO", json, first);
        
        json << "]";
        std::string result = json.str();
        char* cResult = new char[result.length() + 1];
        strcpy_s(cResult, result.length() + 1, result.c_str());
        return cResult;
    }
    
    __declspec(dllexport) BOOL AddStartupEntry(char* section, char* name, char* path) {
        HKEY hBase = HKEY_LOCAL_MACHINE;
        std::string sectionStr = section;
        std::string regPath;
        
        if (sectionStr == "Winlogon") {
            regPath = "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon";
        } else if (sectionStr == "AppInit") {
            regPath = "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Windows";
        } else if (sectionStr == "Run") {
            regPath = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run";
        } else if (sectionStr == "RunOnce") {
            regPath = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\RunOnce";
        } else {
            return FALSE;
        }
        
        HKEY hKey;
        if (RegOpenKeyExA(hBase, regPath.c_str(), 0, KEY_WRITE, &hKey) == ERROR_SUCCESS) {
            LONG result = RegSetValueExA(hKey, name, 0, REG_SZ, 
                                        (BYTE*)path, strlen(path) + 1);
            RegCloseKey(hKey);
            return result == ERROR_SUCCESS;
        }
        
        if (RegOpenKeyExA(HKEY_CURRENT_USER, regPath.c_str(), 0, KEY_WRITE, &hKey) == ERROR_SUCCESS) {
            LONG result = RegSetValueExA(hKey, name, 0, REG_SZ, 
                                        (BYTE*)path, strlen(path) + 1);
            RegCloseKey(hKey);
            return result == ERROR_SUCCESS;
        }
        
        return FALSE;
    }
    
    __declspec(dllexport) BOOL RemoveStartupEntry(char* section, char* name) {
        HKEY hBase = HKEY_LOCAL_MACHINE;
        std::string sectionStr = section;
        std::string regPath;
        
        if (sectionStr == "Winlogon") {
            regPath = "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon";
        } else if (sectionStr == "AppInit") {
            regPath = "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Windows";
        } else if (sectionStr == "Run") {
            regPath = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run";
        } else if (sectionStr == "RunOnce") {
            regPath = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\RunOnce";
        } else {
            return FALSE;
        }
        
        HKEY hKey;
        if (RegOpenKeyExA(hBase, regPath.c_str(), 0, KEY_WRITE, &hKey) == ERROR_SUCCESS) {
            LONG result = RegDeleteValueA(hKey, name);
            RegCloseKey(hKey);
            if (result == ERROR_SUCCESS) return TRUE;
        }
        
        if (RegOpenKeyExA(HKEY_CURRENT_USER, regPath.c_str(), 0, KEY_WRITE, &hKey) == ERROR_SUCCESS) {
            LONG result = RegDeleteValueA(hKey, name);
            RegCloseKey(hKey);
            return result == ERROR_SUCCESS;
        }
        
        return FALSE;
    }

    __declspec(dllexport) BOOL SetStartupValue(char* section, char* name, char* newValue) {
        HKEY hBase = HKEY_LOCAL_MACHINE;
        std::string sectionStr = section;
        std::string regPath;
        
        if (sectionStr == "Winlogon") {
            regPath = "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon";
        } else if (sectionStr == "AppInit") {
            regPath = "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Windows";
        } else if (sectionStr == "Run") {
            regPath = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run";
        } else if (sectionStr == "RunOnce") {
            regPath = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\RunOnce";
        } else {
            return FALSE;
        }
        
        HKEY hKey;
        if (RegOpenKeyExA(hBase, regPath.c_str(), 0, KEY_WRITE, &hKey) == ERROR_SUCCESS) {
            LONG result = RegSetValueExA(hKey, name, 0, REG_SZ, 
                                        (BYTE*)newValue, strlen(newValue) + 1);
            RegCloseKey(hKey);
            return result == ERROR_SUCCESS;
        }
        return FALSE;
    }
    
    __declspec(dllexport) char* GetUsersList() {
        std::stringstream json;
        json << "[";
        BOOL first = TRUE;
        
        LPUSER_INFO_0 pBuf = NULL;
        DWORD entriesRead = 0;
        DWORD totalEntries = 0;
        
        if (NetUserEnum(NULL, 0, FILTER_NORMAL_ACCOUNT, (LPBYTE*)&pBuf, 
                       MAX_PREFERRED_LENGTH, &entriesRead, &totalEntries, NULL) == NERR_Success) {
            for (DWORD i = 0; i < entriesRead; i++) {
                if (!first) json << ",";
                first = FALSE;
                
                WCHAR username[256];
                wcscpy_s(username, pBuf[i].usri0_name);
                
                std::string userName = wchar_to_string(username);
                std::string userType = "User";
                
                USER_INFO_1* pUserInfo = NULL;
                if (NetUserGetInfo(NULL, username, 1, (LPBYTE*)&pUserInfo) == NERR_Success) {
                    if (pUserInfo->usri1_priv == USER_PRIV_ADMIN) {
                        userType = "Admin";
                    }
                    
                    if (pUserInfo->usri1_flags & UF_ACCOUNTDISABLE) {
                        userType = "Disabled";
                    }
                    
                    NetApiBufferFree(pUserInfo);
                }
                
                if (userName == "Administrator" || userName == "Guest") {
                    userType = "System";
                }
                
                json << "{\"name\":\"" << escape_json(userName) 
                     << "\",\"type\":\"" << userType << "\"}";
            }
            NetApiBufferFree(pBuf);
        }
        
        json << "]";
        std::string result = json.str();
        char* cResult = new char[result.length() + 1];
        strcpy_s(cResult, result.length() + 1, result.c_str());
        return cResult;
    }
    
    __declspec(dllexport) BOOL AddUser(char* username, char* password, BOOL isAdmin) {
        USER_INFO_1 ui;
        memset(&ui, 0, sizeof(ui));
        
        WCHAR wUsername[256];
        WCHAR wPassword[256];
        MultiByteToWideChar(CP_UTF8, 0, username, -1, wUsername, 256);
        MultiByteToWideChar(CP_UTF8, 0, password, -1, wPassword, 256);
        
        ui.usri1_name = wUsername;
        ui.usri1_password = wPassword;
        ui.usri1_priv = isAdmin ? USER_PRIV_ADMIN : USER_PRIV_USER;
        ui.usri1_home_dir = NULL;
        ui.usri1_comment = NULL;
        ui.usri1_flags = UF_SCRIPT | UF_NORMAL_ACCOUNT;
        ui.usri1_script_path = NULL;
        
        DWORD dwError = 0;
        NET_API_STATUS nStatus = NetUserAdd(NULL, 1, (LPBYTE)&ui, &dwError);
        return nStatus == NERR_Success;
    }
    
    __declspec(dllexport) BOOL RemoveUser(char* username) {
        WCHAR wUsername[256];
        MultiByteToWideChar(CP_UTF8, 0, username, -1, wUsername, 256);
        return NetUserDel(NULL, wUsername) == NERR_Success;
    }
    
    __declspec(dllexport) char* GetDriversList() {
        std::stringstream json;
        json << "[";
        BOOL first = TRUE;
        
        HKEY hKey;
        if (RegOpenKeyExA(HKEY_LOCAL_MACHINE,
            "SYSTEM\\CurrentControlSet\\Services",
            0, KEY_READ, &hKey) == ERROR_SUCCESS) {
            
            for (int i = 0; ; i++) {
                char serviceName[256];
                DWORD size = sizeof(serviceName);
                
                if (RegEnumKeyExA(hKey, i, serviceName, &size, NULL, NULL, NULL, NULL) != ERROR_SUCCESS) break;
                
                HKEY hServiceKey;
                if (RegOpenKeyExA(hKey, serviceName, 0, KEY_READ, &hServiceKey) == ERROR_SUCCESS) {
                    DWORD type = 0;
                    DWORD typeSize = sizeof(DWORD);
                    
                    if (RegQueryValueExA(hServiceKey, "Type", NULL, NULL, 
                                       (LPBYTE)&type, &typeSize) == ERROR_SUCCESS) {
                        
                        if (type == SERVICE_KERNEL_DRIVER || type == SERVICE_FILE_SYSTEM_DRIVER) {
                            char displayName[256] = "";
                            DWORD displaySize = sizeof(displayName);
                            RegQueryValueExA(hServiceKey, "DisplayName", NULL, NULL,
                                           (LPBYTE)displayName, &displaySize);
                            
                            char imagePath[512] = "";
                            DWORD imageSize = sizeof(imagePath);
                            RegQueryValueExA(hServiceKey, "ImagePath", NULL, NULL,
                                           (LPBYTE)imagePath, &imageSize);
                            
                            if (strlen(displayName) == 0) {
                                strcpy_s(displayName, serviceName);
                            }
                            
                            DWORD startType = 3;
                            DWORD startSize = sizeof(DWORD);
                            RegQueryValueExA(hServiceKey, "Start", NULL, NULL,
                                           (LPBYTE)&startType, &startSize);
                            
                            const char* status = "Stopped";
                            if (startType == 0 || startType == 1) status = "Running";
                            if (startType == 2) status = "Auto";
                            if (startType == 4) status = "Disabled";
                            
                            const char* signature = "Unsigned";
                            
                            if (!first) json << ",";
                            first = FALSE;
                            
                            json << "{\"name\":\"" << escape_json(displayName) 
                                 << "\",\"service\":\"" << escape_json(serviceName)
                                 << "\",\"path\":\"" << escape_json(imagePath)
                                 << "\",\"status\":\"" << status
                                 << "\",\"signed\":\"" << signature << "\"}";
                        }
                    }
                    RegCloseKey(hServiceKey);
                }
            }
            RegCloseKey(hKey);
        }
        
        json << "]";
        std::string result = json.str();
        char* cResult = new char[result.length() + 1];
        strcpy_s(cResult, result.length() + 1, result.c_str());
        return cResult;
    }
    
    __declspec(dllexport) BOOL SetDriverState(char* serviceName, BOOL enable) {
        SC_HANDLE hSCManager = OpenSCManagerA(NULL, NULL, SC_MANAGER_ALL_ACCESS);
        if (!hSCManager) return FALSE;
        
        SC_HANDLE hService = OpenServiceA(hSCManager, serviceName, SERVICE_CHANGE_CONFIG | SERVICE_START | SERVICE_STOP);
        if (!hService) {
            CloseServiceHandle(hSCManager);
            return FALSE;
        }
        
        BOOL result = FALSE;
        if (enable) {
            result = ChangeServiceConfigA(hService, SERVICE_NO_CHANGE, SERVICE_AUTO_START, 
                                         SERVICE_NO_CHANGE, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
            if (result) StartServiceA(hService, 0, NULL);
        } else {
            ControlService(hService, SERVICE_CONTROL_STOP, NULL);
            result = ChangeServiceConfigA(hService, SERVICE_NO_CHANGE, SERVICE_DISABLED, 
                                         SERVICE_NO_CHANGE, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
        }
        
        CloseServiceHandle(hService);
        CloseServiceHandle(hSCManager);
        return result;
    }
    
    __declspec(dllexport) BOOL DeleteDriver(char* serviceName) {
        SC_HANDLE hSCManager = OpenSCManagerA(NULL, NULL, SC_MANAGER_ALL_ACCESS);
        if (!hSCManager) return FALSE;
        
        SC_HANDLE hService = OpenServiceA(hSCManager, serviceName, DELETE);
        if (!hService) {
            CloseServiceHandle(hSCManager);
            return FALSE;
        }
        
        BOOL result = DeleteService(hService);
        CloseServiceHandle(hService);
        CloseServiceHandle(hSCManager);
        return result;
    }
    
    __declspec(dllexport) BOOL AddAutoKillProcess(char* processName) {
        HKEY hKey;
        if (RegOpenKeyExA(HKEY_LOCAL_MACHINE,
            "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon",
            0, KEY_WRITE, &hKey) == ERROR_SUCCESS) {
            
            char killCmd[1024];
            sprintf_s(killCmd, "cmd /c taskkill /F /IM %s >nul 2>&1", processName);
            
            LONG result = RegSetValueExA(hKey, "AutoKill", 0, REG_SZ, 
                                        (BYTE*)killCmd, strlen(killCmd) + 1);
            RegCloseKey(hKey);
            return result == ERROR_SUCCESS;
        }
        return FALSE;
    }

    __declspec(dllexport) char* GetKeyLocks() {
        std::stringstream json;
        json << "{";
        
        BOOL taskMgrDisabled = FALSE;
        BOOL regeditDisabled = FALSE;
        BOOL cmdDisabled = FALSE;
        BOOL ctrlAltDelDisabled = FALSE;
        
        HKEY hKey;
        if (RegOpenKeyExA(HKEY_CURRENT_USER,
            "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System",
            0, KEY_READ, &hKey) == ERROR_SUCCESS) {
            
            DWORD value = 0, size = sizeof(DWORD);
            if (RegQueryValueExA(hKey, "DisableTaskMgr", NULL, NULL, (LPBYTE)&value, &size) == ERROR_SUCCESS) {
                taskMgrDisabled = (value == 1);
            }
            RegCloseKey(hKey);
        }

        if (RegOpenKeyExA(HKEY_LOCAL_MACHINE,
            "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System",
            0, KEY_READ, &hKey) == ERROR_SUCCESS) {
            
            DWORD value = 0, size = sizeof(DWORD);
            if (RegQueryValueExA(hKey, "DisableTaskMgr", NULL, NULL, (LPBYTE)&value, &size) == ERROR_SUCCESS) {
                if (value == 1) taskMgrDisabled = TRUE;
            }
            RegCloseKey(hKey);
        }
        
        if (RegOpenKeyExA(HKEY_CURRENT_USER,
            "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System",
            0, KEY_READ, &hKey) == ERROR_SUCCESS) {
            
            DWORD value = 0, size = sizeof(DWORD);
            if (RegQueryValueExA(hKey, "DisableRegistryTools", NULL, NULL, (LPBYTE)&value, &size) == ERROR_SUCCESS) {
                regeditDisabled = (value == 1);
            }
            RegCloseKey(hKey);
        }

        if (RegOpenKeyExA(HKEY_CURRENT_USER,
            "SOFTWARE\\Policies\\Microsoft\\Windows\\System",
            0, KEY_READ, &hKey) == ERROR_SUCCESS) {
            
            DWORD value = 0, size = sizeof(DWORD);
            if (RegQueryValueExA(hKey, "DisableCMD", NULL, NULL, (LPBYTE)&value, &size) == ERROR_SUCCESS) {
                cmdDisabled = (value == 1);
            }
            RegCloseKey(hKey);
        }

        if (RegOpenKeyExA(HKEY_CURRENT_USER,
            "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System",
            0, KEY_READ, &hKey) == ERROR_SUCCESS) {
            
            DWORD value = 0, size = sizeof(DWORD);
            if (RegQueryValueExA(hKey, "DisableLockWorkstation", NULL, NULL, (LPBYTE)&value, &size) == ERROR_SUCCESS) {
                if (value == 1) ctrlAltDelDisabled = TRUE;
            }
            if (RegQueryValueExA(hKey, "DisableChangePassword", NULL, NULL, (LPBYTE)&value, &size) == ERROR_SUCCESS) {
                if (value == 1) ctrlAltDelDisabled = TRUE;
            }
            RegCloseKey(hKey);
        }
        
        json << "\"taskmgr\":" << (taskMgrDisabled ? "true" : "false")
             << ",\"regedit\":" << (regeditDisabled ? "true" : "false")
             << ",\"cmd\":" << (cmdDisabled ? "true" : "false")
             << ",\"ctrlaltdel\":" << (ctrlAltDelDisabled ? "true" : "false")
             << ",\"ctrlshiftesc\":" << (taskMgrDisabled ? "true" : "false");
        
        json << "}";
        std::string result = json.str();
        char* cResult = new char[result.length() + 1];
        strcpy_s(cResult, result.length() + 1, result.c_str());
        return cResult;
    }

    __declspec(dllexport) BOOL UnlockKey(char* keyName) {
        std::string key = keyName;
        HKEY hKey;
        BOOL result = FALSE;
        
        if (key == "taskmgr" || key == "ctrlshiftesc") {
            if (RegOpenKeyExA(HKEY_CURRENT_USER,
                "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System",
                0, KEY_WRITE, &hKey) == ERROR_SUCCESS) {
                DWORD value = 0;
                RegSetValueExA(hKey, "DisableTaskMgr", 0, REG_DWORD, (LPBYTE)&value, sizeof(DWORD));
                RegCloseKey(hKey);
                result = TRUE;
            }
            if (RegOpenKeyExA(HKEY_LOCAL_MACHINE,
                "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System",
                0, KEY_WRITE, &hKey) == ERROR_SUCCESS) {
                DWORD value = 0;
                RegSetValueExA(hKey, "DisableTaskMgr", 0, REG_DWORD, (LPBYTE)&value, sizeof(DWORD));
                RegCloseKey(hKey);
                result = TRUE;
            }
        } else if (key == "regedit") {
            if (RegOpenKeyExA(HKEY_CURRENT_USER,
                "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System",
                0, KEY_WRITE, &hKey) == ERROR_SUCCESS) {
                RegDeleteValueA(hKey, "DisableRegistryTools");
                RegCloseKey(hKey);
                result = TRUE;
            }
        } else if (key == "cmd") {
            if (RegOpenKeyExA(HKEY_CURRENT_USER,
                "SOFTWARE\\Policies\\Microsoft\\Windows\\System",
                0, KEY_WRITE, &hKey) == ERROR_SUCCESS) {
                RegDeleteValueA(hKey, "DisableCMD");
                RegCloseKey(hKey);
                result = TRUE;
            }
        } else if (key == "ctrlaltdel") {
            if (RegOpenKeyExA(HKEY_CURRENT_USER,
                "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System",
                0, KEY_WRITE, &hKey) == ERROR_SUCCESS) {
                RegDeleteValueA(hKey, "DisableLockWorkstation");
                RegDeleteValueA(hKey, "DisableChangePassword");
                RegCloseKey(hKey);
                result = TRUE;
            }
        }
        
        return result;
    }

    __declspec(dllexport) BOOL SetWallpaper(char* wallpaperPath) {
        return SystemParametersInfoA(SPI_SETDESKWALLPAPER, 0, (PVOID)wallpaperPath, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE);
    }

    __declspec(dllexport) BOOL SetAccentColor(DWORD color) {
        HKEY hKey;
        if (RegOpenKeyExA(HKEY_CURRENT_USER,
            "SOFTWARE\\Microsoft\\Windows\\DWM",
            0, KEY_WRITE, &hKey) == ERROR_SUCCESS) {
            
            RegSetValueExA(hKey, "AccentColor", 0, REG_DWORD, (LPBYTE)&color, sizeof(DWORD));
            RegSetValueExA(hKey, "ColorizationColor", 0, REG_DWORD, (LPBYTE)&color, sizeof(DWORD));
            RegSetValueExA(hKey, "ColorizationAfterglow", 0, REG_DWORD, (LPBYTE)&color, sizeof(DWORD));
            RegCloseKey(hKey);
            return TRUE;
        }
        return FALSE;
    }
    
    __declspec(dllexport) char* GetRegistryKey(char* keyPath) {
        std::stringstream json;
        json << "[";
        BOOL first = TRUE;
        
        HKEY hBaseKey = HKEY_LOCAL_MACHINE;
        std::string path = keyPath;
        std::string actualPath;
        
        if (path.find("HKEY_LOCAL_MACHINE\\") == 0) {
            hBaseKey = HKEY_LOCAL_MACHINE;
            actualPath = path.substr(19);
        } else if (path.find("HKEY_CURRENT_USER\\") == 0) {
            hBaseKey = HKEY_CURRENT_USER;
            actualPath = path.substr(18);
        } else {
            actualPath = path;
        }
        
        HKEY hKey;
        if (RegOpenKeyExA(hBaseKey, actualPath.c_str(), 0, KEY_READ, &hKey) == ERROR_SUCCESS) {
            for (int i = 0; ; i++) {
                char subKeyName[256];
                DWORD size = sizeof(subKeyName);
                
                if (RegEnumKeyExA(hKey, i, subKeyName, &size, NULL, NULL, NULL, NULL) != ERROR_SUCCESS) break;
                
                if (!first) json << ",";
                first = FALSE;
                json << "{\"name\":\"" << escape_json(subKeyName) << "\",\"type\":\"Key\",\"value\":\"\"}";
            }
            
            for (int i = 0; ; i++) {
                char valueName[256];
                DWORD nameSize = sizeof(valueName);
                DWORD type;
                char data[1024];
                DWORD dataSize = sizeof(data);
                
                LONG result = RegEnumValueA(hKey, i, valueName, &nameSize, NULL, &type, 
                                          (LPBYTE)data, &dataSize);
                if (result != ERROR_SUCCESS) break;
                
                if (!first) json << ",";
                first = FALSE;
                
                std::string typeStr;
                switch(type) {
                    case REG_SZ: typeStr = "REG_SZ"; break;
                    case REG_DWORD: typeStr = "REG_DWORD"; break;
                    case REG_BINARY: typeStr = "REG_BINARY"; break;
                    case REG_MULTI_SZ: typeStr = "REG_MULTI_SZ"; break;
                    case REG_EXPAND_SZ: typeStr = "REG_EXPAND_SZ"; break;
                    default: typeStr = "REG_" + std::to_string(type);
                }
                
                std::string valueStr;
                if (type == REG_DWORD) {
                    DWORD dwordValue = *(DWORD*)data;
                    valueStr = std::to_string(dwordValue);
                } else if (type == REG_SZ || type == REG_EXPAND_SZ) {
                    valueStr = data;
                } else {
                    valueStr = "(binary data)";
                }
                
                json << "{\"name\":\"" << escape_json(valueName) 
                     << "\",\"type\":\"" << typeStr 
                     << "\",\"value\":\"" << escape_json(valueStr) << "\"}";
            }
            RegCloseKey(hKey);
        }
        
        json << "]";
        std::string result = json.str();
        char* cResult = new char[result.length() + 1];
        strcpy_s(cResult, result.length() + 1, result.c_str());
        return cResult;
    }
    
    __declspec(dllexport) BOOL SetRegistryValue(char* keyPath, char* valueName, char* newValue) {
        std::string path = keyPath;
        HKEY hBaseKey = HKEY_LOCAL_MACHINE;
        std::string actualPath;
        
        if (path.find("HKEY_LOCAL_MACHINE\\") == 0) {
            hBaseKey = HKEY_LOCAL_MACHINE;
            actualPath = path.substr(19);
        } else if (path.find("HKEY_CURRENT_USER\\") == 0) {
            hBaseKey = HKEY_CURRENT_USER;
            actualPath = path.substr(18);
        } else {
            actualPath = path;
        }
        
        HKEY hKey;
        if (RegOpenKeyExA(hBaseKey, actualPath.c_str(), 0, KEY_WRITE, &hKey) == ERROR_SUCCESS) {
            LONG result = RegSetValueExA(hKey, valueName, 0, REG_SZ, 
                                        (BYTE*)newValue, strlen(newValue) + 1);
            RegCloseKey(hKey);
            return result == ERROR_SUCCESS;
        }
        return FALSE;
    }
    
    __declspec(dllexport) char* GetProcessList() {
        std::stringstream json;
        json << "[";
        BOOL first = TRUE;
        
        HANDLE hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
        if (hSnapshot != INVALID_HANDLE_VALUE) {
            PROCESSENTRY32 pe32;
            pe32.dwSize = sizeof(PROCESSENTRY32);
            
            if (Process32First(hSnapshot, &pe32)) {
                do {
                    if (!first) json << ",";
                    first = FALSE;
                    
                    const char* processType = "User";
                    if (pe32.th32ProcessID == 0 || pe32.th32ProcessID == 4) {
                        processType = "System";
                    } else {
                        HANDLE hProcess = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, 
                                                     FALSE, pe32.th32ProcessID);
                        if (hProcess) {
                            char processPath[MAX_PATH];
                            DWORD pathSize = sizeof(processPath);
                            if (QueryFullProcessImageNameA(hProcess, 0, processPath, &pathSize)) {
                                if (strstr(processPath, "\\System32\\") || 
                                    strstr(processPath, "\\SysWOW64\\")) {
                                    if (strstr(processPath, "svchost.exe") ||
                                        strstr(processPath, "winlogon.exe") ||
                                        strstr(processPath, "csrss.exe") ||
                                        strstr(processPath, "smss.exe") ||
                                        strstr(processPath, "services.exe") ||
                                        strstr(processPath, "lsass.exe")) {
                                        processType = "System";
                                    }
                                }
                            }
                            CloseHandle(hProcess);
                        }
                    }
                    
                    HANDLE hProcess = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, 
                                                 FALSE, pe32.th32ProcessID);
                    double memoryMB = 0;
                    if (hProcess) {
                        PROCESS_MEMORY_COUNTERS pmc;
                        if (GetProcessMemoryInfo(hProcess, &pmc, sizeof(pmc))) {
                            memoryMB = pmc.WorkingSetSize / (1024.0 * 1024.0);
                        }
                        CloseHandle(hProcess);
                    }
                    
                    json << "{\"name\":\"" << escape_json(pe32.szExeFile) 
                         << "\",\"pid\":" << pe32.th32ProcessID
                         << ",\"threads\":" << pe32.cntThreads
                         << ",\"memory\":" << memoryMB
                         << ",\"type\":\"" << processType << "\"}";
                } while (Process32Next(hSnapshot, &pe32));
            }
            CloseHandle(hSnapshot);
        }
        
        json << "]";
        std::string result = json.str();
        char* cResult = new char[result.length() + 1];
        strcpy_s(cResult, result.length() + 1, result.c_str());
        return cResult;
    }
    
    __declspec(dllexport) BOOL KillProcess(DWORD pid) {
        if (pid == 0 || pid == 4) return FALSE;
        
        HANDLE hProcess = OpenProcess(PROCESS_TERMINATE, FALSE, pid);
        if (hProcess == NULL) return FALSE;
        
        BOOL result = TerminateProcess(hProcess, 1);
        CloseHandle(hProcess);
        return result;
    }
    
    __declspec(dllexport) char* GetFileList(char* directoryPath) {
        std::stringstream json;
        json << "[";
        BOOL first = TRUE;
        
        char searchPath[MAX_PATH];
        sprintf_s(searchPath, "%s\\*", directoryPath);
        
        WIN32_FIND_DATAA findData;
        HANDLE hFind = FindFirstFileA(searchPath, &findData);
        
        if (hFind != INVALID_HANDLE_VALUE) {
            do {
                if (strcmp(findData.cFileName, ".") == 0 || 
                    strcmp(findData.cFileName, "..") == 0) continue;
                
                if (!first) json << ",";
                first = FALSE;
                
                const char* type = (findData.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) ? 
                                  "Directory" : "File";
                DWORD size = (findData.nFileSizeHigh * (MAXDWORD + 1)) + findData.nFileSizeLow;
                double sizeKB = size / 1024.0;
                
                json << "{\"name\":\"" << escape_json(findData.cFileName) 
                     << "\",\"type\":\"" << type
                     << "\",\"size\":" << sizeKB << "}";
            } while (FindNextFileA(hFind, &findData));
            FindClose(hFind);
        }
        
        json << "]";
        std::string result = json.str();
        char* cResult = new char[result.length() + 1];
        strcpy_s(cResult, result.length() + 1, result.c_str());
        return cResult;
    }
    
    __declspec(dllexport) void FreeString(char* str) {
        if (str) delete[] str;
    }
}

BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved) {
    return TRUE;
}