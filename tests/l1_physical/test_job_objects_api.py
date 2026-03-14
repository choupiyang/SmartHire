"""
测试 Job Objects API 正确用法
"""
import win32job
import win32con
import sys
import io

# 设置标准输出为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 测试 1: 创建 Job Object
print("测试 1: 创建 Job Object")
try:
    job_handle = win32job.CreateJobObject(None, "TestJob")
    print(f"  [OK] Job Object 创建成功: {job_handle}")
except Exception as e:
    print(f"  [FAIL] Job Object 创建失败: {e}")
    exit(1)

# 测试 2: 查询 Job Object 信息
print("\n测试 2: 查询 Job Object 信息")
try:
    # 尝试查询基本信息
    info = win32job.QueryInformationJobObject(job_handle, win32job.JobObjectBasicAccountingInformation)
    print(f"  [OK] 查询成功: {type(info)}")
except Exception as e:
    print(f"  [WARN] 查询失败: {e}")

# 测试 3: 使用完整嵌套字典设置信息
print("\n测试 3: 使用完整嵌套字典设置信息")
try:
    # 方法 1: 完整的嵌套字典（包含所有必需字段）
    extended_info = {
        'BasicLimitInformation': {
            'PerProcessUserTimeLimit': 0,
            'PerJobUserTimeLimit': 0,
            'LimitFlags': win32job.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE,
            'MinimumWorkingSetSize': 0,
            'MaximumWorkingSetSize': 0,
            'ActiveProcessLimit': 0,
            'Affinity': 0,
            'PriorityClass': 32,
            'SchedulingClass': 5
        },
        'IoInfo': {
            'ReadOperationCount': 0,
            'WriteOperationCount': 0,
            'OtherOperationCount': 0,
            'ReadTransferCount': 0,
            'WriteTransferCount': 0,
            'OtherTransferCount': 0
        },
        'ProcessMemoryLimit': 0,
        'JobMemoryLimit': 0,
        'PeakProcessMemoryUsed': 0,
        'PeakJobMemoryUsed': 0
    }
    win32job.SetInformationJobObject(
        job_handle,
        win32job.JobObjectExtendedLimitInformation,
        extended_info
    )
    print(f"  [OK] 完整嵌套字典设置成功")
except Exception as e:
    print(f"  [FAIL] 完整嵌套字典设置失败: {e}")

# 测试 4: 验证设置是否成功
print("\n测试 4: 验证设置是否成功")
try:
    info = win32job.QueryInformationJobObject(job_handle, win32job.JobObjectExtendedLimitInformation)
    limit_flags = info['BasicLimitInformation']['LimitFlags']
    has_kill_on_close = bool(limit_flags & win32job.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE)
    print(f"  [OK] 查询成功")
    print(f"  LimitFlags: {limit_flags}")
    print(f"  KILL_ON_JOB_CLOSE: {has_kill_on_close}")
    if has_kill_on_close:
        print(f"  [OK] KILL_ON_JOB_CLOSE 配置成功")
    else:
        print(f"  [FAIL] KILL_ON_JOB_CLOSE 配置失败")
except Exception as e:
    print(f"  [FAIL] 验证失败: {e}")

# 测试 5: 查询扩展信息
print("\n测试 5: 查询扩展信息")
try:
    info = win32job.QueryInformationJobObject(job_handle, win32job.JobObjectExtendedLimitInformation)
    print(f"  [OK] 查询成功: {type(info)}")
    print(f"  内容: {info}")
except Exception as e:
    print(f"  [WARN] 查询失败: {e}")

# 清理
try:
    import win32api
    win32api.CloseHandle(job_handle)
    print("\n[OK] 所有测试完成")
except ImportError:
    print("\n[OK] 所有测试完成（未清理 handle）")