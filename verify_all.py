import subprocess
import sys
import os

print("=== YOUTUBE DESKTOP: END-TO-END VERIFICATION SCRIPT ===")

def run_step(name, command):
    print(f"\n[{name}] Running: {' '.join(command)}")
    result = subprocess.run(command, text=True, capture_output=True)
    if result.returncode != 0:
        print(f"❌ FAILED: {name}")
        print(f"STDOUT:\n{result.stdout}")
        print(f"STDERR:\n{result.stderr}")
        sys.exit(1)
    else:
        print(f"✅ PASSED: {name}")

# Step 1: Install Dependencies
run_step("Install Dependencies", [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

# Step 2: Check for Broken Requirements
run_step("Check Packages", [sys.executable, "-m", "pip", "check"])

# Make sure we don't open windows during test
env = os.environ.copy()
env['QT_QPA_PLATFORM'] = 'offscreen'
env['PYTHONPATH'] = os.path.join(os.getcwd(), 'src')

# Run internal tests
print("\n[Running Internal Tests]")
result_t1 = subprocess.run([sys.executable, "test_script.py"], env=env, text=True, capture_output=True)
if result_t1.returncode != 0:
    print(f"❌ FAILED: test_script.py\n{result_t1.stderr}")
    sys.exit(1)
print("✅ PASSED: test_script.py")

result_t2 = subprocess.run([sys.executable, "test_script2.py"], env=env, text=True, capture_output=True)
if result_t2.returncode != 0:
    print(f"❌ FAILED: test_script2.py\n{result_t2.stderr}")
    sys.exit(1)
print("✅ PASSED: test_script2.py")

print("\n🎉 ALL VERIFICATION STEPS COMPLETED SUCCESSFULLY!")
