from main import is_premium, check_and_update_usage
import json
import os

# Create dummy files for testing
with open("premium_users.json", "w") as f:
    json.dump(["premium_user_1"], f)

# Reset usage
if os.path.exists("user_usage.json"):
    os.remove("user_usage.json")

print("Test 1: Premium User Check")
assert is_premium("premium_user_1") == True, "Premium user not detected"
assert is_premium("regular_user") == False, "Regular user falsely detected as premium"
print("PASS")

print("Test 2: Usage Limit (Premium)")
# Should always return True without updating usage file for limit
assert check_and_update_usage("premium_user_1") == True
assert check_and_update_usage("premium_user_1") == True
print("PASS")

print("Test 3: Usage Limit (Regular)")
# First time allow
assert check_and_update_usage("regular_user") == True
# Second time deny
assert check_and_update_usage("regular_user") == False
print("PASS")

print("ALL TESTS PASSED")
