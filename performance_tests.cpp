#include <windows.h>
#include <string>
#include <sstream>
#include <vector>
#include <thread>
#include <chrono>
#include <random>
#include <algorithm>

#pragma comment(lib, "psapi.lib")

extern "C" {
    struct TestResult {
        double score;
        std::string details;
    };

    __declspec(dllexport) char* RunCPUBenchmark() {
        auto start = std::chrono::high_resolution_clock::now();
        
        const int iterations = 100000000;
        double result = 0.0;

        for (int i = 0; i < iterations; i++) {
            result += sin(i) * cos(i) + sqrt(i + 1);
        }

        int primes = 0;
        for (int n = 2; n < 10000; n++) {
            bool isPrime = true;
            for (int i = 2; i * i <= n; i++) {
                if (n % i == 0) {
                    isPrime = false;
                    break;
                }
            }
            if (isPrime) primes++;
        }
        
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
        
        double score = 1000000.0 / duration.count();
        
        std::stringstream json;
        json << "{\"score\":" << score 
             << ",\"time_ms\":" << duration.count()
             << ",\"primes_found\":" << primes
             << ",\"iterations\":" << iterations
             << ",\"details\":\"CPU Benchmark completed in " << duration.count() << "ms\"}";
        
        std::string resultStr = json.str();
        char* cResult = new char[resultStr.length() + 1];
        strcpy_s(cResult, resultStr.length() + 1, resultStr.c_str());
        return cResult;
    }

    __declspec(dllexport) char* RunRAMBenchmark() {
        const size_t size = 100 * 1024 * 1024;
        char* data = new char[size];

        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_int_distribution<> dis(0, 255);
        
        auto start = std::chrono::high_resolution_clock::now();
        
        for (size_t i = 0; i < size; i++) {
            data[i] = dis(gen);
        }

        volatile long long sum = 0;
        for (size_t i = 0; i < size; i++) {
            sum += data[i];
        }

        char* copy = new char[size];
        memcpy(copy, data, size);
        
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
        
        double bandwidthMBps = (size * 3.0) / (1024.0 * 1024.0) / (duration.count() / 1000.0);
        double score = bandwidthMBps / 1000.0;
        
        delete[] data;
        delete[] copy;
        
        std::stringstream json;
        json << "{\"score\":" << score 
             << ",\"bandwidth_mbps\":" << bandwidthMBps
             << ",\"time_ms\":" << duration.count()
             << ",\"size_mb\":" << (size / (1024.0 * 1024.0))
             << ",\"details\":\"RAM Bandwidth: " << bandwidthMBps << " MB/s\"}";
        
        std::string resultStr = json.str();
        char* cResult = new char[resultStr.length() + 1];
        strcpy_s(cResult, resultStr.length() + 1, resultStr.c_str());
        return cResult;
    }

    static bool stressTestRunning = false;
    static std::vector<std::thread> stressThreads;
    
    __declspec(dllexport) char* StartStressTest() {
        if (stressTestRunning) {
            std::string result = "{\"status\":\"already_running\",\"details\":\"Stress test is already running\"}";
            char* cResult = new char[result.length() + 1];
            strcpy_s(cResult, result.length() + 1, result.c_str());
            return cResult;
        }
        
        stressTestRunning = true;
        stressThreads.clear();

        SYSTEM_INFO sysInfo;
        GetSystemInfo(&sysInfo);
        int numCores = sysInfo.dwNumberOfProcessors;

        for (int i = 0; i < numCores; i++) {
            stressThreads.emplace_back([i]() {
                std::random_device rd;
                std::mt19937 gen(rd() + i);
                std::uniform_int_distribution<> dis(1, 1000000);
                
                volatile double sum = 0.0;
                while (stressTestRunning) {
                    for (int j = 0; j < 1000000; j++) {
                        sum += sin(dis(gen)) * cos(dis(gen));
                    }

                    std::this_thread::sleep_for(std::chrono::microseconds(100));
                }
            });
        }
        
        std::stringstream json;
        json << "{\"status\":\"started\",\"threads\":" << numCores 
             << ",\"details\":\"Stress test started on " << numCores << " cores\"}";
        
        std::string resultStr = json.str();
        char* cResult = new char[resultStr.length() + 1];
        strcpy_s(cResult, resultStr.length() + 1, resultStr.c_str());
        return cResult;
    }
    
    __declspec(dllexport) char* StopStressTest() {
        if (!stressTestRunning) {
            std::string result = "{\"status\":\"not_running\",\"details\":\"No stress test is running\"}";
            char* cResult = new char[result.length() + 1];
            strcpy_s(cResult, result.length() + 1, result.c_str());
            return cResult;
        }
        
        stressTestRunning = false;

        for (auto& thread : stressThreads) {
            if (thread.joinable()) {
                thread.join();
            }
        }
        stressThreads.clear();
        
        std::string result = "{\"status\":\"stopped\",\"details\":\"Stress test stopped successfully\"}";
        char* cResult = new char[result.length() + 1];
        strcpy_s(cResult, result.length() + 1, result.c_str());
        return cResult;
    }
    
    __declspec(dllexport) char* GetStressTestStatus() {
        std::stringstream json;
        json << "{\"running\":" << (stressTestRunning ? "true" : "false");
        
        if (stressTestRunning) {
            FILETIME idleTime, kernelTime, userTime;
            if (GetSystemTimes(&idleTime, &kernelTime, &userTime)) {
                static ULONGLONG lastIdleTime = 0;
                static ULONGLONG lastKernelTime = 0;
                static ULONGLONG lastUserTime = 0;
                
                ULONGLONG idle = ((ULONGLONG)idleTime.dwHighDateTime << 32) | idleTime.dwLowDateTime;
                ULONGLONG kernel = ((ULONGLONG)kernelTime.dwHighDateTime << 32) | kernelTime.dwLowDateTime;
                ULONGLONG user = ((ULONGLONG)userTime.dwHighDateTime << 32) | userTime.dwLowDateTime;
                
                if (lastIdleTime > 0) {
                    ULONGLONG idleDiff = idle - lastIdleTime;
                    ULONGLONG kernelDiff = kernel - lastKernelTime;
                    ULONGLONG userDiff = user - lastUserTime;
                    ULONGLONG totalDiff = kernelDiff + userDiff;
                    
                    if (totalDiff > 0) {
                        double cpuUsage = 100.0 * (1.0 - (double)idleDiff / (double)totalDiff);
                        if (cpuUsage < 0) cpuUsage = 0;
                        if (cpuUsage > 100) cpuUsage = 100;
                        json << ",\"cpu_usage\":" << cpuUsage;
                    }
                }
                
                lastIdleTime = idle;
                lastKernelTime = kernel;
                lastUserTime = user;
            }

            MEMORYSTATUSEX memStatus;
            memStatus.dwLength = sizeof(MEMORYSTATUSEX);
            if (GlobalMemoryStatusEx(&memStatus)) {
                double totalGB = memStatus.ullTotalPhys / (1024.0 * 1024.0 * 1024.0);
                double usedGB = (memStatus.ullTotalPhys - memStatus.ullAvailPhys) / (1024.0 * 1024.0 * 1024.0);
                double memoryUsage = (usedGB / totalGB) * 100.0;
                
                json << ",\"memory_usage\":" << memoryUsage
                     << ",\"memory_used_gb\":" << usedGB
                     << ",\"memory_total_gb\":" << totalGB;
            }
        }
        
        json << "}";
        
        std::string resultStr = json.str();
        char* cResult = new char[resultStr.length() + 1];
        strcpy_s(cResult, resultStr.length() + 1, resultStr.c_str());
        return cResult;
    }

    __declspec(dllexport) char* RunFullBenchmark() {
        std::stringstream json;
        json << "{";

        char* cpuResult = RunCPUBenchmark();
        json << "\"cpu\":" << cpuResult << ",";
        delete[] cpuResult;

        char* ramResult = RunRAMBenchmark();
        json << "\"ram\":" << ramResult;
        delete[] ramResult;
        
        json << "}";
        
        std::string resultStr = json.str();
        char* cResult = new char[resultStr.length() + 1];
        strcpy_s(cResult, resultStr.length() + 1, resultStr.c_str());
        return cResult;
    }
    
    __declspec(dllexport) void FreeString(char* str) {
        if (str) delete[] str;
    }
}

BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved) {
    switch (ul_reason_for_call) {
    case DLL_PROCESS_DETACH:
        if (stressTestRunning) {
            stressTestRunning = false;
            for (auto& thread : stressThreads) {
                if (thread.joinable()) {
                    thread.join();
                }
            }
            stressThreads.clear();
        }
        break;
    }
    return TRUE;
}
