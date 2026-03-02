# Translation Files

This directory contains JSON translation files for the Nyaya Mitra UI elements.

## Supported Languages

- **en.json** - English (Base language)
- **hi.json** - Hindi (हिन्दी)
- **ta.json** - Tamil (தமிழ்)
- **te.json** - Telugu (తెలుగు)
- **bn.json** - Bengali (বাংলা)
- **mr.json** - Marathi (मराठी)
- **gu.json** - Gujarati (ગુજરાતી)

## File Structure

Each translation file is a JSON object with key-value pairs where:
- **Key**: Translation identifier (e.g., "app_name", "login", "submit")
- **Value**: Translated text in the target language

Example:
```json
{
  "app_name": "Nyaya Mitra",
  "welcome": "Welcome to Nyaya Mitra",
  "login": "Login"
}
```

## Translation Categories

The translations are organized into the following categories:

### Common UI Elements
- Basic actions: login, register, submit, cancel, save, delete, edit
- Navigation: back, next, previous, search, filter, clear
- Status messages: loading, error, success

### Feature-Specific Translations

1. **Chat Interface**
   - chat_title, chat_placeholder, send_message
   - new_conversation, conversation_history

2. **Case Analysis**
   - case_analysis, validity_score, evidence_strength
   - legal_basis, procedural_compliance, timeline_analysis
   - weaknesses, recommendations

3. **Document Generation**
   - document_generator, select_template
   - legal_letter, rti_application, counter_petition
   - generate_document, download_pdf, download_text

4. **Legal Aid**
   - legal_aid, find_legal_aid, location
   - specialization, contact_info, phone, address

5. **Emergency**
   - emergency, emergency_contacts
   - police, legal_helpline, mental_health, student_services

6. **Evidence Guide**
   - evidence_guide, collect_evidence
   - digital_evidence, physical_evidence

7. **Settings**
   - settings, language, change_language
   - profile, account

## Legal Term Consistency

All translations maintain consistent legal terminology across features to ensure:
- Accuracy in legal context
- User comprehension
- Professional presentation

Key legal terms are carefully translated to preserve their legal meaning in each language.

## Adding New Translations

To add a new translation key:

1. Add the key-value pair to **en.json** (base language)
2. Add corresponding translations to all other language files
3. Ensure legal terms are accurately translated
4. Test the translation in the application

Example:
```json
// en.json
"new_feature": "New Feature"

// hi.json
"new_feature": "नई सुविधा"

// ta.json
"new_feature": "புதிய அம்சம்"
```

## Usage in Code

The translation service automatically loads these JSON files at startup:

```python
from translation_service import get_translation_service

service = get_translation_service()

# Get a single translation
text = service.get_translation("login", language="hi")

# Get all translations for a language
all_translations = service.get_all_translations(language="ta")
```

## Maintenance

- Review translations regularly for accuracy
- Update legal terminology when laws change
- Ensure consistency across all language files
- Test translations with native speakers when possible

## Notes

- All files use UTF-8 encoding to support Unicode characters
- JSON format allows easy integration with frontend frameworks
- Separate files enable easier management and updates compared to embedded translations
- Each language file is independent, allowing for easy addition of new languages
