import requests
import sys
import json
from datetime import datetime, timedelta

class MedicalEquipmentAPITester:
    def __init__(self, base_url="https://492b379c-7e7c-4642-8f79-dc5faedf8bb3.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.created_equipment_id = None
        self.created_maintenance_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, form_data=None):
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
                if form_data:
                    # For form-urlencoded data (like login)
                    response = requests.post(url, data=form_data, headers=headers)
                else:
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

    def test_root_endpoint(self):
        """Test the root endpoint"""
        return self.run_test(
            "Root Endpoint",
            "GET",
            "/api/",
            200
        )

    def test_health_endpoint(self):
        """Test the health check endpoint"""
        return self.run_test(
            "Health Check Endpoint",
            "GET",
            "/api/health",
            200
        )

    def test_login_with_valid_credentials(self):
        """Test login with valid credentials using form-urlencoded data"""
        form_data = {
            "username": "admin",
            "password": "admin"
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        success, response = self.run_test(
            "Login with Valid Credentials (admin/admin)",
            "POST",
            "/api/login",
            200,
            headers=headers,
            form_data=form_data
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            print(f"Token received: {self.token[:10]}...")
            return True
        return False

    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials"""
        form_data = {
            "username": "wrong",
            "password": "wrong"
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        return self.run_test(
            "Login with Invalid Credentials",
            "POST",
            "/api/login",
            401,
            headers=headers,
            form_data=form_data
        )[0]

    def test_me_endpoint(self):
        """Test the /api/me endpoint to get current user info"""
        if not self.token:
            print("❌ No token available, skipping /api/me test")
            return False
        
        return self.run_test(
            "Get Current User Info",
            "GET",
            "/api/me",
            200
        )[0]

    def test_list_equipments(self):
        """Test listing all equipments"""
        if not self.token:
            print("❌ No token available, skipping equipment listing test")
            return False
        
        return self.run_test(
            "List All Equipments",
            "GET",
            "/api/equipamentos",
            200
        )[0]

    def test_create_equipment(self):
        """Test creating a new equipment"""
        if not self.token:
            print("❌ No token available, skipping equipment creation test")
            return False
        
        equipment_data = {
            "nome": f"Equipamento de Teste {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "tipo": "Respirador",
            "modelo": "Modelo de Teste",
            "numero_serie": f"SN-TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "fabricante": "Fabricante de Teste",
            "data_aquisicao": datetime.now().isoformat(),
            "data_ultima_manutencao": (datetime.now() - timedelta(days=30)).isoformat(),
            "status": "ativo",
            "localizacao": "Sala de Testes",
            "departamento": "Departamento de Testes"
        }
        
        success, response = self.run_test(
            "Create New Equipment",
            "POST",
            "/api/equipamentos",
            201,
            data=equipment_data
        )
        
        if success and 'equipamento' in response and 'id' in response['equipamento']:
            self.created_equipment_id = response['equipamento']['id']
            print(f"Created equipment with ID: {self.created_equipment_id}")
            return True
        return False

    def test_list_maintenances(self):
        """Test listing all maintenances"""
        if not self.token:
            print("❌ No token available, skipping maintenance listing test")
            return False
        
        return self.run_test(
            "List All Maintenances",
            "GET",
            "/api/manutencoes",
            200
        )[0]

    def test_create_maintenance(self):
        """Test creating a new maintenance"""
        if not self.token or not self.created_equipment_id:
            print("❌ No token or equipment ID available, skipping maintenance creation test")
            return False
        
        maintenance_data = {
            "equipamento_id": self.created_equipment_id,
            "tipo": "preventiva",
            "descricao": f"Manutenção de teste criada em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "data_agendada": datetime.now().isoformat(),
            "data_prevista": (datetime.now() + timedelta(days=7)).isoformat(),
            "status": "pendente",
            "tecnico": "Técnico de Teste",
            "observacoes": "Observações de teste para a manutenção"
        }
        
        success, response = self.run_test(
            "Create New Maintenance",
            "POST",
            "/api/manutencoes",
            201,
            data=maintenance_data
        )
        
        if success and 'manutencao' in response and 'id' in response['manutencao']:
            self.created_maintenance_id = response['manutencao']['id']
            print(f"Created maintenance with ID: {self.created_maintenance_id}")
            return True
        return False

    def test_reports_endpoint(self):
        """Test the reports endpoint"""
        if not self.token:
            print("❌ No token available, skipping reports test")
            return False
        
        return self.run_test(
            "Get Reports",
            "GET",
            "/api/relatorios",
            200
        )[0]

    def test_notifications_endpoint(self):
        """Test the notifications endpoint"""
        if not self.token:
            print("❌ No token available, skipping notifications test")
            return False
        
        return self.run_test(
            "Get Notifications",
            "GET",
            "/api/notificacoes",
            200
        )[0]

def main():
    # Setup
    tester = MedicalEquipmentAPITester()
    
    # Run basic tests
    root_success = tester.test_root_endpoint()
    health_success = tester.test_health_endpoint()
    invalid_login_success = tester.test_login_with_invalid_credentials()
    valid_login_success = tester.test_login_with_valid_credentials()
    
    # Tests that require a valid token
    if valid_login_success:
        me_success = tester.test_me_endpoint()
        list_equipments_success = tester.test_list_equipments()
        create_equipment_success = tester.test_create_equipment()
        list_maintenances_success = tester.test_list_maintenances()
        create_maintenance_success = tester.test_create_maintenance()
        reports_success = tester.test_reports_endpoint()
        notifications_success = tester.test_notifications_endpoint()
    else:
        print("❌ Login failed, skipping token-dependent tests")
        me_success = False
        list_equipments_success = False
        create_equipment_success = False
        list_maintenances_success = False
        create_maintenance_success = False
        reports_success = False
        notifications_success = False

    # Print results
    print(f"\n📊 Tests Summary:")
    print(f"Root Endpoint: {'✅' if root_success else '❌'}")
    print(f"Health Check: {'✅' if health_success else '❌'}")
    print(f"Invalid Login: {'✅' if invalid_login_success else '❌'}")
    print(f"Valid Login: {'✅' if valid_login_success else '❌'}")
    print(f"User Info (/api/me): {'✅' if me_success else '❌'}")
    print(f"List Equipments: {'✅' if list_equipments_success else '❌'}")
    print(f"Create Equipment: {'✅' if create_equipment_success else '❌'}")
    print(f"List Maintenances: {'✅' if list_maintenances_success else '❌'}")
    print(f"Create Maintenance: {'✅' if create_maintenance_success else '❌'}")
    print(f"Reports: {'✅' if reports_success else '❌'}")
    print(f"Notifications: {'✅' if notifications_success else '❌'}")
    
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    
    # Return exit code based on test results
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())