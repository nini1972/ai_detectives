import requests
import sys
import os
import json
import time
from datetime import datetime

class VisualSystemTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.case_id = None
        self.session_id = None
        self.character_id = None
        self.character_name = None

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
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
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_content = response.json()
                    print(f"Error response: {error_content}")
                except:
                    print(f"Error response: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_generate_case(self):
        """Test case generation"""
        success, response = self.run_test(
            "Generate Case",
            "POST",
            "api/generate-case",
            200
        )
        
        if success and 'case' in response:
            self.case_id = response['case']['id']
            self.session_id = response.get('session_id')
            print(f"Generated case ID: {self.case_id}")
            print(f"Session ID: {self.session_id}")
            
            # Find a character for testing
            if response['case']['characters'] and len(response['case']['characters']) > 0:
                self.character_id = response['case']['characters'][0]['id']
                self.character_name = response['case']['characters'][0]['name']
                print(f"Selected character for testing: {self.character_name}")
            
            return True, response['case']
        return False, None

    def test_get_case(self):
        """Test retrieving a case"""
        if not self.case_id:
            print("❌ No case ID available for testing")
            return False, None
            
        success, response = self.run_test(
            "Get Case",
            "GET",
            f"api/cases/{self.case_id}",
            200
        )
        
        if success and 'case' in response:
            print(f"Retrieved case title: {response['case']['title']}")
            return True, response['case']
        return False, None

    def test_crime_scene_image_generation(self, max_attempts=6, delay=10):
        """Test crime scene image generation with polling"""
        print(f"\n🔍 Testing Crime Scene Image Generation...")
        self.tests_run += 1
        
        for attempt in range(1, max_attempts + 1):
            print(f"Checking for crime scene image (attempt {attempt}/{max_attempts})...")
            
            success, case = self.test_get_case()
            if not success:
                print("❌ Failed to retrieve case")
                return False, None
            
            if case.get('crime_scene_image_url'):
                print(f"✅ Crime scene image generated successfully after {attempt} attempts")
                print(f"Image URL: {case['crime_scene_image_url']}")
                self.tests_passed += 1
                return True, case['crime_scene_image_url']
            
            if attempt < max_attempts:
                print(f"Image not ready yet, waiting {delay} seconds...")
                time.sleep(delay)
        
        print("❌ Failed - Crime scene image was not generated within the time limit")
        return False, None

    def test_question_character_with_visual_trigger(self, question):
        """Test questioning a character with a visual trigger phrase"""
        if not self.case_id or not self.character_id:
            print("❌ No case or character available for testing")
            return False, None, False
        
        success, response = self.run_test(
            f"Question Character with Visual Trigger: '{question}'",
            "POST",
            "api/question-character",
            200,
            data={
                "case_id": self.case_id,
                "character_id": self.character_id,
                "question": question
            }
        )
        
        if success:
            # Check if a visual scene was generated
            visual_scene_generated = False
            if response.get('visual_scene_generated'):
                print(f"✅ Visual scene generated from testimony!")
                print(f"Scene URL: {response['visual_scene_generated']['image_url']}")
                visual_scene_generated = True
            else:
                print("ℹ️ No visual scene was generated from this question")
            
            return True, response, visual_scene_generated
        
        return False, None, False

    def test_get_visual_scenes(self):
        """Test retrieving visual scenes for a case"""
        if not self.case_id:
            print("❌ No case ID available for testing")
            return False, []
            
        success, response = self.run_test(
            "Get Visual Scenes",
            "GET",
            f"api/case-scenes/{self.case_id}",
            200
        )
        
        if success and 'scenes' in response:
            scenes_count = len(response['scenes'])
            print(f"Found {scenes_count} visual scenes")
            return True, response['scenes']
        return False, []

def main():
    # Get the backend URL from environment or use the one from frontend/.env
    backend_url = os.environ.get("BACKEND_URL")
    
    if not backend_url:
        try:
            with open('/app/frontend/.env', 'r') as f:
                for line in f:
                    if line.startswith('REACT_APP_BACKEND_URL='):
                        backend_url = line.strip().split('=')[1]
                        break
        except Exception as e:
            print(f"Error reading .env file: {e}")
    
    if not backend_url:
        print("❌ No backend URL found. Please set BACKEND_URL environment variable.")
        return 1
        
    print(f"Using backend URL: {backend_url}")
    
    # Setup tester
    tester = VisualSystemTester(backend_url)
    
    # Run tests
    print("\n🔍 Starting Visual System Tests for Detective Game\n")
    
    # Generate a new case
    case_success, case = tester.test_generate_case()
    if not case_success:
        print("❌ Case generation failed, stopping tests")
        return 1
    
    # Test crime scene image generation (with polling)
    print("\n🏛️ Testing Crime Scene Image Auto-Refresh...")
    image_success, image_url = tester.test_crime_scene_image_generation()
    
    # Test visual scene generation through character questioning
    if tester.character_id:
        print("\n📸 Testing Testimony Visual Scene Generation...")
        
        # Test questions that should trigger visual scenes
        visual_trigger_questions = [
            "What exactly did you see that night?",
            "Describe what happened in detail",
            "Tell me about the confrontation"
        ]
        
        visual_scenes_generated = 0
        
        for question in visual_trigger_questions:
            question_success, response, scene_generated = tester.test_question_character_with_visual_trigger(question)
            
            if scene_generated:
                visual_scenes_generated += 1
        
        print(f"\nVisual scenes generated from testimony: {visual_scenes_generated}/{len(visual_trigger_questions)}")
    
    # Get all visual scenes for the case
    print("\n🎬 Testing Visual Gallery...")
    scenes_success, scenes = tester.test_get_visual_scenes()
    
    # Print results
    print("\n" + "=" * 50)
    print("📊 VISUAL SYSTEM TEST RESULTS")
    print("=" * 50)
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print(f"🏛️ Crime scene image generated: {'Yes' if image_success else 'No'}")
    print(f"🎬 Visual scenes in gallery: {len(scenes)}")
    print("=" * 50)
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())