"""
Test if the MCP server can run standalone
"""
import subprocess
import sys
import time

print("Testing MCP server standalone...")
print("=" * 60)

# Start the server
proc = subprocess.Popen(
    [sys.executable, "providers/cdm_db/provider.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Give it 2 seconds to start
time.sleep(2)

# Check if it's still running
if proc.poll() is None:
    print("✅ Server process is running")
    print(f"   PID: {proc.pid}")
    
    # Try to send an initialization message
    try:
        init_msg = '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}\n'
        proc.stdin.write(init_msg)
        proc.stdin.flush()
        print("✅ Sent initialization message")
        
        # Wait for response
        time.sleep(2)
        
    except Exception as e:
        print(f"❌ Error sending message: {e}")
    
    # Kill the process
    proc.terminate()
    proc.wait(timeout=5)
    print("✅ Server terminated cleanly")
else:
    # Process died
    returncode = proc.poll()
    stdout, stderr = proc.communicate()
    print(f"❌ Server process died immediately")
    print(f"   Return code: {returncode}")
    if stdout:
        print(f"   STDOUT: {stdout}")
    if stderr:
        print(f"   STDERR: {stderr}")

print("=" * 60)

