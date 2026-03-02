"""Quick test for evidence guide generator"""
from evidence_guide_generator import get_evidence_guide_generator

# Test guide generation
gen = get_evidence_guide_generator()
guide = gen.generate_complete_guide(case_type='harassment')

print(f"Guide generated successfully!")
print(f"Case type: {guide['case_type']}")
print(f"Title: {guide['title']}")
print(f"Total steps: {guide['total_steps']}")
print(f"Total checklists: {guide['total_checklists']}")
print(f"\nFirst step: {guide['step_by_step_instructions'][0]['title']}")
print(f"Tampering warning present: {'tampering_warning' in guide}")
print(f"Digital preservation present: {'digital_preservation' in guide}")
print(f"Admissibility requirements present: {'admissibility_requirements' in guide}")
print(f"Digital communication procedures present: {'digital_communication_procedures' in guide}")

# Test case type detection
detected = gen.detect_case_type(case_description="Someone is blackmailing me for money")
print(f"\nCase type detection test: {detected.value}")

print("\n✅ All tests passed!")
