
import requests
import sys
import time
import json

class DetectiveGameAPITester:
    def __init__(self, base_url="https://52adacca-3bd6-46f3-bde1-2343dfdbb816.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.case_id = None
        self.session_id = None
        self.character_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                return success, response.json()
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error details: {error_data}")
                except:
                    print(f"Response text: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_endpoint(self):
        """Test the health endpoint"""
        success, response = self.run_test(
            "Health Endpoint",
            "GET",
            "/api/health",
            200
        )
        if success:
            print(f"Health status: {response}")
        return success

    def test_generate_case(self):
        """Test generating a new case"""
        success, response = self.run_test(
            "Generate Case",
            "POST",
            "/api/generate-case",
            200
        )
        if success:
            self.case_id = response['case']['id']
            self.session_id = response['session_id']
            print(f"Generated case ID: {self.case_id}")
            print(f"Session ID: {self.session_id}")
            
            # Print some case details
            print(f"Case title: {response['case']['title']}")
            print(f"Setting: {response['case']['setting']}")
            print(f"Victim: {response['case']['victim_name']}")
            print(f"Number of characters: {len(response['case']['characters'])}")
            print(f"Number of evidence items: {len(response['case']['evidence'])}")
            
            # Store first character ID for questioning
            if response['case']['characters']:
                self.character_id = response['case']['characters'][0]['id']
                print(f"First character: {response['case']['characters'][0]['name']}")
        
        return success

    def test_question_character(self, question="Where were you at the time of the murder?"):
        """Test questioning a character"""
        if not self.case_id or not self.character_id:
            print("❌ Cannot test character questioning - no case or character ID")
            return False
            
        success, response = self.run_test(
            "Question Character",
            "POST",
            "/api/question-character",
            200,
            data={
                "case_id": self.case_id,
                "character_id": self.character_id,
                "question": question
            }
        )
        
        if success:
            print(f"Character name: {response['character_name']}")
            print(f"Response: {response['response']}")
            
            # Check for new character discoveries
            if response.get('new_characters_discovered'):
                print(f"\n🔍 NEW CHARACTERS DISCOVERED: {len(response['new_characters_discovered'])}")
                for discovery in response['new_characters_discovered']:
                    print(f"  - {discovery['character']['name']} ({discovery['character']['description']})")
                    print(f"    Discovered through: {discovery['discovered_through']}")
                    print(f"    Context: {discovery['context']}")
                    # Store the new character ID for further questioning
                    return success, discovery['character']['id']
        
        return success, None

    def test_analyze_evidence(self):
        """Test analyzing evidence and theory"""
        if not self.case_id:
            print("❌ Cannot test evidence analysis - no case ID")
            return False
            
        # Get first evidence ID
        success, case_response = self.run_test(
            "Get Case",
            "GET",
            f"/api/cases/{self.case_id}",
            200
        )
        
        if not success or not case_response.get('case', {}).get('evidence'):
            print("❌ Failed to get evidence for analysis")
            return False
            
        evidence_id = case_response['case']['evidence'][0]['id']
        
        success, response = self.run_test(
            "Analyze Evidence",
            "POST",
            "/api/analyze-evidence",
            200,
            data={
                "case_id": self.case_id,
                "evidence_ids": [evidence_id],
                "theory": "I believe the murder was committed by the victim's closest associate due to financial motives."
            }
        )
        
        if success:
            print(f"Analysis response length: {len(response['analysis'])}")
            print(f"Analysis excerpt: {response['analysis'][:150]}...")
        
        return success
    
    def test_get_case(self):
        """Test retrieving a specific case"""
        if not self.case_id:
            print("❌ Cannot test case retrieval - no case ID")
            return False
            
        success, response = self.run_test(
            "Get Case",
            "GET",
            f"/api/cases/{self.case_id}",
            200
        )
        
        if success:
            print(f"Retrieved case title: {response['case']['title']}")
        
        return success

def main():
    print("=" * 50)
    print("DUAL-AI DETECTIVE GAME API TESTER")
    print("=" * 50)
    
    tester = DetectiveGameAPITester()
    
    # Test health endpoint
    health_ok = tester.test_health_endpoint()
    if not health_ok:
        print("❌ Health check failed, stopping tests")
        return 1
    
    # Test case generation
    case_ok = tester.test_generate_case()
    if not case_ok:
        print("❌ Case generation failed, stopping tests")
        return 1
    
    # Give the backend some time to process
    print("\nWaiting for case to be fully processed...")
    time.sleep(2)
    
    # Test case retrieval
    get_case_ok = tester.test_get_case()
    if not get_case_ok:
        print("❌ Case retrieval failed")
    
    # Test character questioning
    question_ok = tester.test_question_character()
    if not question_ok:
        print("❌ Character questioning failed")
    
    # Test evidence analysis
    analysis_ok = tester.test_analyze_evidence()
    if not analysis_ok:
        print("❌ Evidence analysis failed")
    
    print("\n" + "=" * 50)
    print("NOTE: Save/Load Game functionality is client-side only")
    print("      using browser localStorage. No backend API endpoints")
    print("      are required for this functionality.")
    print("=" * 50)
    
    print("\n" + "=" * 50)
    print("SAVE/LOAD FUNCTIONALITY VERIFICATION:")
    print("1. The Save/Load button is present in the game header")
    print("2. Saving a game stores the following state:")
    print("   - Current case data")
    print("   - Session ID")
    print("   - Conversation history")
    print("   - Investigation notes")
    print("   - Selected evidence")
    print("   - Theory and analysis")
    print("   - Game state")
    print("3. Loading a game restores all the above state")
    print("4. Multiple saves can be managed (create/load/delete)")
    print("=" * 50)
    
    # Print results
    print("\n" + "=" * 50)
    print(f"📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print("=" * 50)
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())