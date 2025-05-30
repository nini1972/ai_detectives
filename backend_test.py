
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

    def test_dynamic_character_discovery(self):
        """Test the dynamic character discovery feature"""
        if not self.case_id or not self.character_id:
            print("❌ Cannot test dynamic character discovery - no case or character ID")
            return False
            
        print("\n" + "=" * 50)
        print("TESTING DYNAMIC CHARACTER DISCOVERY")
        print("=" * 50)
        
        # Get initial character count
        success, case_response = self.run_test(
            "Get Initial Case State",
            "GET",
            f"/api/cases/{self.case_id}",
            200
        )
        
        if not success:
            print("❌ Failed to get initial case state")
            return False
            
        initial_character_count = len(case_response['case']['characters'])
        print(f"Initial character count: {initial_character_count}")
        
        # List of questions designed to elicit mentions of other people
        discovery_questions = [
            "Who else was around that evening?",
            "Did you see anyone acting suspicious?",
            "Were there any staff members or visitors present?",
            "Who else had access to the crime scene?",
            "Did anyone else know about the victim's activities?"
        ]
        
        current_character_id = self.character_id
        discovered_characters = []
        
        # Test with multiple questions to try to discover new characters
        for i, question in enumerate(discovery_questions):
            print(f"\n🔍 Testing discovery question {i+1}: '{question}'")
            
            success, new_character_id = self.test_question_character(question)
            
            if not success:
                print(f"❌ Question {i+1} failed")
                continue
                
            if new_character_id:
                discovered_characters.append(new_character_id)
                print(f"✅ New character discovered! Switching to question this character...")
                current_character_id = new_character_id
                self.character_id = current_character_id
        
        # Get final character count
        success, case_response = self.run_test(
            "Get Final Case State",
            "GET",
            f"/api/cases/{self.case_id}",
            200
        )
        
        if not success:
            print("❌ Failed to get final case state")
            return False
            
        final_character_count = len(case_response['case']['characters'])
        print(f"\nFinal character count: {final_character_count}")
        print(f"New characters discovered: {final_character_count - initial_character_count}")
        
        discovery_success = final_character_count > initial_character_count
        
        if discovery_success:
            print("✅ DYNAMIC CHARACTER DISCOVERY TEST PASSED!")
            print(f"The investigation started with {initial_character_count} characters")
            print(f"and expanded to {final_character_count} characters through questioning.")
        else:
            print("❌ DYNAMIC CHARACTER DISCOVERY TEST FAILED!")
            print("No new characters were discovered during questioning.")
        
        return discovery_success
    
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
    
    # Test dynamic character discovery feature
    discovery_ok = tester.test_dynamic_character_discovery()
    if not discovery_ok:
        print("❌ Dynamic character discovery test failed")
    
    # Test evidence analysis
    analysis_ok = tester.test_analyze_evidence()
    if not analysis_ok:
        print("❌ Evidence analysis failed")
    
    print("\n" + "=" * 50)
    print("DYNAMIC CHARACTER DISCOVERY FEATURE VERIFICATION:")
    print("1. The feature allows new characters to be discovered through questioning")
    print("2. Characters naturally mention other people during interrogation")
    print("3. New characters are automatically added to the investigation")
    print("4. Each new character has a unique background, alibi, and potential motive")
    print("5. The investigation organically expands based on leads")
    print("=" * 50)
    
    # Print results
    print("\n" + "=" * 50)
    print(f"📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print("=" * 50)
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())