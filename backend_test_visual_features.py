import requests
import sys
import time
import os
from datetime import datetime

class VisualDetectiveGameTester:
    def __init__(self, base_url=None):
        # Get the backend URL from environment or use the one from frontend/.env
        if not base_url:
            try:
                with open('/app/frontend/.env', 'r') as f:
                    for line in f:
                        if line.startswith('REACT_APP_BACKEND_URL='):
                            base_url = line.strip().split('=')[1].strip('"\'')
                            break
            except Exception as e:
                print(f"Error reading .env file: {e}")
                
        if not base_url:
            raise ValueError("No backend URL found. Please provide a base_url parameter.")
            
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.case_id = None
        self.session_id = None
        self.character_id = None
        self.character_name = None
        self.visual_scenes = []
        
        print(f"Using backend URL: {self.base_url}")

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
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
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_content = response.json()
                    print(f"Error response: {error_content}")
                except:
                    print(f"Error response: {response.text}")

            try:
                return success, response.json()
            except:
                return success, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_endpoint(self):
        """Test the health endpoint"""
        success, response = self.run_test(
            "Health Endpoint",
            "GET",
            "health",
            200
        )
        if success:
            print(f"Health status: {response}")
        return success

    def test_generate_case(self):
        """Test case generation with crime scene image"""
        print("\n==================================================")
        print("TESTING CASE GENERATION WITH CRIME SCENE IMAGE")
        print("==================================================")
        
        success, response = self.run_test(
            "Generate Case",
            "POST",
            "generate-case",
            200,
            data={}
        )
        if success:
            self.case_id = response.get('case', {}).get('id')
            self.session_id = response.get('session_id')
            case_data = response.get('case', {})
            
            print(f"Generated case ID: {self.case_id}")
            print(f"Session ID: {self.session_id}")
            print(f"Case title: {case_data.get('title')}")
            print(f"Setting: {case_data.get('setting')}")
            print(f"Victim: {case_data.get('victim_name')}")
            print(f"Number of characters: {len(case_data.get('characters', []))}")
            print(f"Number of evidence items: {len(case_data.get('evidence', []))}")
            
            # Check for crime scene image URL in initial response
            if case_data.get('crime_scene_image_url'):
                print(f"✅ Crime scene image already generated: {case_data.get('crime_scene_image_url')}")
            else:
                print(f"⚠️ No crime scene image in initial response - this is expected as it's generated asynchronously")
            
            if case_data.get('characters'):
                self.character_id = case_data['characters'][0]['id']
                self.character_name = case_data['characters'][0]['name']
                print(f"First character: {self.character_name}")
            
            # Wait for case to be fully processed and crime scene image to be generated
            print("\nWaiting for crime scene image generation (30 seconds)...")
            time.sleep(30)
            
            # Check if crime scene image was generated after waiting
            success, updated_case = self.run_test(
                "Get Updated Case",
                "GET",
                f"cases/{self.case_id}",
                200
            )
            
            if success:
                updated_case_data = updated_case.get('case', {})
                if updated_case_data.get('crime_scene_image_url'):
                    print(f"✅ Crime scene image generated successfully: {updated_case_data.get('crime_scene_image_url')}")
                    return True
                else:
                    print(f"❌ Crime scene image not generated after waiting")
                    return False
            
        return success

    def test_visual_testimony_system(self):
        """Test the visual testimony system with trigger phrases"""
        print("\n==================================================")
        print("TESTING VISUAL TESTIMONY SYSTEM")
        print("==================================================")
        
        if not self.case_id or not self.character_id:
            print("❌ No case ID or character ID available for testing")
            return False
        
        # First check the initial state
        success, response = self.run_test(
            "Get Initial Case State",
            "GET",
            f"cases/{self.case_id}",
            200
        )
        if success:
            case_data = response.get('case', {})
            initial_scenes_count = len(case_data.get('visual_scenes', []))
            print(f"Initial visual scenes count: {initial_scenes_count}")
            
            # Store the crime scene image URL for verification
            crime_scene_url = case_data.get('crime_scene_image_url')
            if crime_scene_url:
                print(f"Crime scene image URL: {crime_scene_url}")
            else:
                print("❌ No crime scene image URL found")
        
        # Test visual trigger phrases
        visual_trigger_phrases = [
            "What exactly did you see that night?",
            "Describe the confrontation in detail",
            "Tell me what happened when you found the body",
            "What did the scene look like when you arrived?"
        ]
        
        scenes_generated = 0
        for i, phrase in enumerate(visual_trigger_phrases):
            print(f"\n🔍 Testing visual trigger phrase {i+1}: '{phrase}'")
            
            success, response = self.run_test(
                "Question Character",
                "POST",
                "question-character",
                200,
                data={
                    "case_id": self.case_id,
                    "character_id": self.character_id,
                    "question": phrase
                }
            )
            
            if success:
                print(f"Character name: {response.get('character_name')}")
                print(f"Response excerpt: {response.get('response')[:100]}...")
                
                # Check for visual scene generation
                if response.get('visual_scene_generated'):
                    scene = response.get('visual_scene_generated')
                    scenes_generated += 1
                    
                    print(f"\n🎬 VISUAL SCENE GENERATED!")
                    print(f"  - Title: {scene.get('title')}")
                    print(f"  - Description: {scene.get('description')[:100]}...")
                    print(f"  - Image URL: {scene.get('image_url')}")
                    print(f"  - Generated from: {scene.get('generated_from')}")
                    print(f"  - Character involved: {scene.get('character_involved')}")
                    
                    # Add to our list of visual scenes
                    self.visual_scenes.append(scene)
                else:
                    print(f"❌ No visual scene generated from this question")
            
            # Wait a bit between questions to avoid rate limiting
            time.sleep(5)
        
        # Final check of visual scenes
        success, response = self.run_test(
            "Get Final Case State",
            "GET",
            f"cases/{self.case_id}",
            200
        )
        if success:
            case_data = response.get('case', {})
            final_scenes_count = len(case_data.get('visual_scenes', []))
            print(f"\nFinal visual scenes count: {final_scenes_count}")
            print(f"New scenes generated during test: {final_scenes_count - initial_scenes_count}")
            
            if final_scenes_count > initial_scenes_count:
                print("✅ Visual testimony system is working!")
                return True
            else:
                print("❌ No new visual scenes were generated")
                return False
        
        return scenes_generated > 0

    def test_visual_gallery(self):
        """Test the visual gallery API"""
        print("\n==================================================")
        print("TESTING VISUAL GALLERY API")
        print("==================================================")
        
        if not self.case_id:
            print("❌ No case ID available for testing")
            return False
            
        success, response = self.run_test(
            "Get Case Scenes",
            "GET",
            f"case-scenes/{self.case_id}",
            200
        )
        if success:
            scenes = response.get('scenes', [])
            print(f"Retrieved {len(scenes)} visual scenes from the gallery API")
            
            if len(scenes) > 0:
                print("\nScene details:")
                for i, scene in enumerate(scenes[:3]):  # Show first 3 scenes
                    print(f"\nScene {i+1}:")
                    print(f"  - Title: {scene.get('title')}")
                    print(f"  - Description: {scene.get('description')[:100]}...")
                    print(f"  - Generated from: {scene.get('generated_from')}")
                    print(f"  - Character involved: {scene.get('character_involved')}")
                
                return True
            else:
                print("❌ No scenes found in the gallery")
                return False
        
        return False

    def test_save_and_load_game(self):
        """Test that visual scenes persist when saving and loading a game"""
        # This would be tested in the frontend with Playwright
        print("\n==================================================")
        print("SAVE/LOAD PERSISTENCE WOULD BE TESTED IN FRONTEND")
        print("==================================================")
        return True

def main():
    print("==================================================")
    print("VISUAL DETECTIVE GAME FEATURE TESTER")
    print("==================================================")
    
    tester = VisualDetectiveGameTester()
    
    # Test health endpoint
    if not tester.test_health_endpoint():
        print("❌ Health endpoint test failed, stopping tests")
        return 1
    
    # Test case generation with crime scene image
    if not tester.test_generate_case():
        print("❌ Case generation test failed, stopping tests")
        return 1
    
    # Test the visual testimony system
    if not tester.test_visual_testimony_system():
        print("❌ Visual testimony system test failed")
        # Continue with other tests even if this fails
    
    # Test the visual gallery API
    if not tester.test_visual_gallery():
        print("❌ Visual gallery API test failed")
        # Continue with other tests even if this fails
    
    # Print results
    print("\n==================================================")
    print(f"TESTS PASSED: {tester.tests_passed}/{tester.tests_run}")
    print("==================================================")
    
    # Summary of visual features
    print("\nVISUAL FEATURES SUMMARY:")
    print("1. Crime Scene Image: " + ("✅ Working" if tester.case_id and tester.run_test("Get Case", "GET", f"cases/{tester.case_id}", 200)[1].get('case', {}).get('crime_scene_image_url') else "❌ Not Working"))
    print("2. Testimony Visual Scenes: " + ("✅ Working" if len(tester.visual_scenes) > 0 else "❌ Not Working"))
    print("3. Visual Gallery API: " + ("✅ Working" if tester.test_visual_gallery() else "❌ Not Working"))
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())