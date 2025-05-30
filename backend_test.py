import requests
import sys
import json

class AuthAPITester:
    def __init__(self, base_url="https://492b379c-7e7c-4642-8f79-dc5faedf8bb3.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        if self.token and 'Authorization' not in headers:
            headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)

            print(f"Status Code: {response.status_code}")
            try:
                print(f"Response: {json.dumps(response.json(), indent=2)}")
            except:
                print(f"Response: {response.text}")

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")

            return success, response.json() if 'application/json' in response.headers.get('Content-Type', '') else {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_welcome_endpoint(self):
        """Test the welcome endpoint"""
        return self.run_test(
            "Welcome Endpoint",
            "GET",
            "/api/",
            200
        )

    def test_login_with_valid_credentials(self):
        """Test login with valid credentials"""
        success, response = self.run_test(
            "Login with Valid Credentials (admin/admin)",
            "POST",
            "/api/login",
            200,
            data={"username": "admin", "password": "admin"}
        )
        if success and 'access_token' in response:
            self.token = response['access_token']
            print(f"Token received: {self.token[:10]}...")
            return True
        return False

    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials"""
        return self.run_test(
            "Login with Invalid Credentials",
            "POST",
            "/api/login",
            401,
            data={"username": "wrong", "password": "wrong"}
        )[0]

    def test_dashboard_with_token(self):
        """Test accessing dashboard with valid token"""
        if not self.token:
            print("❌ No token available, skipping dashboard test")
            return False
        
        return self.run_test(
            "Access Dashboard with Token",
            "GET",
            "/api/dashboard",
            200
        )[0]

    def test_dashboard_without_token(self):
        """Test accessing dashboard without token"""
        return self.run_test(
            "Access Dashboard without Token",
            "GET",
            "/api/dashboard",
            401,
            headers={'Content-Type': 'application/json'}  # No Authorization header
        )[0]

    def test_verify_token(self):
        """Test token verification endpoint"""
        if not self.token:
            print("❌ No token available, skipping token verification test")
            return False
        
        return self.run_test(
            "Verify Token",
            "GET",
            "/api/verify-token",
            200
        )[0]

def main():
    # Setup
    tester = AuthAPITester()
    
    # Run tests
    welcome_success = tester.test_welcome_endpoint()
    invalid_login_success = tester.test_login_with_invalid_credentials()
    valid_login_success = tester.test_login_with_valid_credentials()
    dashboard_without_token_success = tester.test_dashboard_without_token()
    
    # Tests that require a valid token
    if valid_login_success:
        verify_token_success = tester.test_verify_token()
        dashboard_with_token_success = tester.test_dashboard_with_token()
    else:
        print("❌ Login failed, skipping token-dependent tests")
        verify_token_success = False
        dashboard_with_token_success = False

    # Print results
    print(f"\n📊 Tests Summary:")
    print(f"Welcome Endpoint: {'✅' if welcome_success else '❌'}")
    print(f"Invalid Login: {'✅' if invalid_login_success else '❌'}")
    print(f"Valid Login: {'✅' if valid_login_success else '❌'}")
    print(f"Dashboard without Token: {'✅' if dashboard_without_token_success else '❌'}")
    print(f"Verify Token: {'✅' if verify_token_success else '❌'}")
    print(f"Dashboard with Token: {'✅' if dashboard_with_token_success else '❌'}")
    
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    
    # Return exit code based on test results
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())