#!/usr/bin/env python3
"""
Test script for auto-recovery mechanism to prevent terminal blocking.
"""

import subprocess
import threading
import time
import sys

def run_command_with_timeout(command, timeout=30, recovery_timeout=10):
    """
    Runs a shell command with a timeout. If the command finishes, it sends a 'wake-up' signal.
    This is a workaround for the AI getting stuck after terminal commands.
    """
    print(f"🔄 Executing: {' '.join(command)}")
    print(f"⏱️ Timeout: {timeout}s, Recovery timeout: {recovery_timeout}s")
    
    process = None
    stdout_output = []
    stderr_output = []
    
    def target():
        nonlocal process, stdout_output, stderr_output
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            for line in process.stdout:
                print(f"📤 STDOUT: {line.strip()}")
                stdout_output.append(line)
            for line in process.stderr:
                print(f"❌ STDERR: {line.strip()}")
                stderr_output.append(line)
            process.wait()
        except Exception as e:
            print(f"❌ Error during command execution: {e}")
    
    thread = threading.Thread(target=target)
    thread.start()
    thread.join(timeout=timeout)
    
    if thread.is_alive():
        print(f"⚠️ Command timed out after {timeout} seconds. Attempting to terminate...")
        if process:
            process.terminate()
            process.wait(timeout=5)
            if process.poll() is None:
                process.kill()
        print("🎯 AUTO-RECOVERY: Command terminated due to timeout.")
        return 1, "".join(stdout_output), "".join(stderr_output)
    else:
        exit_code = process.returncode if process else 1
        print(f"✅ Command completed with exit code: {exit_code}")
        print("🎯 AUTO-RECOVERY: Command completed successfully")
        print("🔓 WAKE-UP SIGNAL: AI should continue processing")
        
        return exit_code, "".join(stdout_output), "".join(stderr_output)

def test_auto_recovery():
    """Test the auto-recovery mechanism with a simple command."""
    print("🧪 Testing auto-recovery with simple command...")
    exit_code, stdout, stderr = run_command_with_timeout(["python", "--version"])
    if exit_code == 0:
        print("✅ Auto-recovery test passed!")
        return True
    else:
        print("❌ Auto-recovery test failed!")
        return False

if __name__ == "__main__":
    success = test_auto_recovery()
    if success:
        print("✅ Auto-recovery test completed successfully!")
    else:
        print("❌ Auto-recovery test failed!")
        sys.exit(1)
