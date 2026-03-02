"""Test evidence guide endpoint"""
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Test 1: Get evidence guide with explicit case type
print("Test 1: Get evidence guide for harassment case")
response = client.get("/api/evidence/guide?case_type=harassment&language=en")
print(f"Status: {response.status_code}")
assert response.status_code == 200, f"Expected 200, got {response.status_code}"

data = response.json()
print(f"Case type: {data['case_type']}")
print(f"Title: {data['title']}")
print(f"Total steps: {data['total_steps']}")
print(f"Total checklists: {data['total_checklists']}")
assert data['case_type'] == 'harassment'
assert data['total_steps'] >= 5  # At least 5 steps
assert data['total_checklists'] >= 2  # At least 2 checklists
print("✅ Test 1 passed\n")

# Test 2: Get evidence guide with case description
print("Test 2: Get evidence guide with case description")
response = client.get("/api/evidence/guide?case_description=Someone is threatening me for money")
print(f"Status: {response.status_code}")
assert response.status_code == 200

data = response.json()
print(f"Detected case type: {data['case_type']}")
assert data['case_type'] in ['extortion', 'general']
print("✅ Test 2 passed\n")

# Test 3: Verify all required sections are present
print("Test 3: Verify all required sections")
response = client.get("/api/evidence/guide?case_type=defamation")
data = response.json()

required_sections = [
    'tampering_warning',
    'case_specific_guidance',
    'step_by_step_instructions',
    'digital_preservation',
    'digital_communication_procedures',
    'admissibility_requirements',
    'evidence_checklists'
]

for section in required_sections:
    assert section in data, f"Missing section: {section}"
    print(f"✓ {section} present")

print("✅ Test 3 passed\n")

# Test 4: Verify step-by-step format with visual aids
print("Test 4: Verify step-by-step format")
steps = data['step_by_step_instructions']
assert len(steps) >= 5, "Should have at least 5 steps"
for i, step in enumerate(steps[:3]):
    assert 'step_number' in step
    assert 'title' in step
    assert 'instruction' in step
    assert step['step_number'] == i + 1
    print(f"✓ Step {step['step_number']}: {step['title']}")
print("✅ Test 4 passed\n")

# Test 5: Verify evidence checklists have at least 5 items
print("Test 5: Verify evidence checklists")
checklists = data['evidence_checklists']
for checklist in checklists:
    assert len(checklist['items']) >= 5, f"Checklist {checklist['title']} has less than 5 items"
    print(f"✓ {checklist['title']}: {len(checklist['items'])} items")
print("✅ Test 5 passed\n")

# Test 6: Get list of case types
print("Test 6: Get list of case types")
response = client.get("/api/evidence/case-types")
assert response.status_code == 200
case_types = response.json()
print(f"Available case types: {', '.join(case_types)}")
assert len(case_types) >= 7  # Should have at least 7 case types
print("✅ Test 6 passed\n")

# Test 7: Invalid case type
print("Test 7: Invalid case type handling")
response = client.get("/api/evidence/guide?case_type=invalid_type")
print(f"Status: {response.status_code}")
assert response.status_code == 400, "Should return 400 for invalid case type"
print("✅ Test 7 passed\n")

print("=" * 50)
print("🎉 All tests passed successfully!")
print("=" * 50)
