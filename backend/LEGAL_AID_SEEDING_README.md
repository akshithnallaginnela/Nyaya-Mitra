# Legal Aid Provider Database Seeding

This document explains how to seed the legal aid provider database with comprehensive data covering legal aid organizations across India.

## Overview

The seeding system consists of:
1. **Seed Data File** (`legal_aid_providers_seed_data.json`) - Contains 40 legal aid providers across India
2. **Seeding Script** (`seed_legal_aid_providers.py`) - Loads and populates the database
3. **Test Suite** (`test_seed_legal_aid_providers.py`) - Validates seed data structure and content

## Seed Data Coverage

The seed data includes:

### Geographic Coverage
- **20+ States**: Delhi, Maharashtra, Karnataka, Tamil Nadu, West Bengal, Telangana, Gujarat, Rajasthan, Punjab, Uttar Pradesh, Kerala, Madhya Pradesh, Andhra Pradesh, Odisha, Bihar, Assam, Jharkhand, Chhattisgarh, Uttarakhand, Himachal Pradesh, Goa, Chandigarh
- **Major Cities**: New Delhi, Mumbai, Bangalore, Chennai, Kolkata, Hyderabad, Ahmedabad, Pune, Jaipur, Lucknow, Kochi, and more

### Organization Types
- **Government**: State Legal Services Authorities (SLSA)
- **NGO**: Legal aid societies and foundations
- **Law Firms**: Pro bono legal services

### Specializations
- Criminal Law
- Civil Law
- Family Law
- Consumer Rights
- Labour Law
- Property Disputes
- Women's Rights
- Child Rights
- Cyber Crime

### Languages Supported
- English
- Hindi
- Regional languages: Tamil, Telugu, Marathi, Bengali, Gujarati, Kannada, Malayalam, Punjabi, Urdu, Odia, Assamese, Konkani, Rajasthani

### Contact Information
Each provider includes:
- Organization name
- Contact phone number
- Contact email address
- Physical address
- City and state
- Website (where applicable)
- Verification status

## Usage

### Prerequisites

1. Ensure PostgreSQL is running
2. Database connection is configured in `.env` file
3. Virtual environment is activated

### Running the Seeding Script

```bash
# Navigate to backend directory
cd backend

# Run the seeding script
python seed_legal_aid_providers.py
```

The script will:
1. Create database tables if they don't exist
2. Load seed data from JSON file
3. Clear existing legal aid provider data (optional)
4. Populate the database with new data
5. Display verification report with statistics

### Expected Output

```
============================================================
LEGAL AID PROVIDER DATABASE SEEDING
============================================================

Creating database tables...
✓ Database tables ready

Loading seed data...
✓ Loaded 40 legal aid providers from legal_aid_providers_seed_data.json

Seeding database...
✓ Cleared 0 existing legal aid provider records
  Processed 10/40 providers...
  Processed 20/40 providers...
  Processed 30/40 providers...
  Processed 40/40 providers...

✓ Successfully seeded 40 legal aid providers

============================================================
VERIFICATION REPORT
============================================================

Total providers in database: 40

Providers by organization type:
  Government: 28
  NGO: 12

Top 10 states by provider count:
  Maharashtra: 4
  Tamil Nadu: 3
  ...

Verification status:
  Verified: 40
  Unverified: 0

Sample providers (first 5):
  ...

============================================================

✓ Seeding completed successfully!
```

### Running Tests

```bash
# Run all seeding tests
pytest test_seed_legal_aid_providers.py -v

# Run specific test
pytest test_seed_legal_aid_providers.py::test_seed_data_coverage -v
```

## Seed Data File Format

The `legal_aid_providers_seed_data.json` file contains an array of provider objects:

```json
[
  {
    "name": "National Legal Services Authority (NALSA)",
    "organization_type": "Government",
    "specializations": ["Criminal Law", "Civil Law", "Family Law"],
    "languages_supported": ["English", "Hindi"],
    "contact_phone": "011-23388952",
    "contact_email": "nalsa@nic.in",
    "website": "https://nalsa.gov.in",
    "address": "Supreme Court of India, Tilak Marg",
    "city": "New Delhi",
    "state": "Delhi",
    "is_verified": true
  }
]
```

### Required Fields
- `name`: Provider or organization name
- `organization_type`: Must be one of: NGO, Government, Law Firm, Legal Aid Society, Bar Association, University Legal Clinic, Pro Bono Service, Community Legal Center, Other
- `specializations`: Array of legal specializations
- `languages_supported`: Array of supported languages
- `city`: City location
- `state`: State location

### Optional Fields
- `contact_phone`: Phone number
- `contact_email`: Email address
- `website`: Website URL
- `address`: Physical address
- `is_verified`: Verification status (defaults to false)

## Modifying Seed Data

To add or update providers:

1. Edit `legal_aid_providers_seed_data.json`
2. Follow the JSON format above
3. Ensure all required fields are present
4. Run tests to validate: `pytest test_seed_legal_aid_providers.py`
5. Run seeding script to populate database

## Error Handling

The seeding script handles various error scenarios:

- **Missing required fields**: Provider is skipped, error is logged
- **Invalid organization type**: Provider is skipped, error is logged
- **Invalid email format**: Provider is skipped, error is logged
- **Invalid phone format**: Provider is skipped, error is logged
- **Database connection errors**: Script exits with error message

All errors are displayed at the end of seeding with details about which providers failed.

## Database Schema

The `LegalAidProvider` model includes:

```python
class LegalAidProvider(BaseModel):
    id: UUID (primary key)
    name: String(255)
    organization_type: String(100) [indexed]
    specializations: Text (JSON string)
    languages_supported: Text (JSON string)
    contact_phone: String(20)
    contact_email: String(255)
    address: Text
    city: String(100) [indexed]
    state: String(100) [indexed]
    is_verified: Boolean
    created_at: DateTime
    updated_at: DateTime
```

### Indexes
- `city`: For location-based searches
- `state`: For state-level searches
- `organization_type`: For filtering by type
- Composite index on `(city, state)`: For combined location searches

## Integration with Legal Aid Search

The seeded data is used by the legal aid search system (Task 13.2) to:
- Search providers by location (city, state)
- Filter by case type/specialization
- Filter by language support
- Display contact information
- Provide fallback to national helplines

## Requirements Validation

This seeding system validates **Requirement 5.5**:
> THE Platform SHALL maintain an updated database of verified Legal_Aid_Providers across India

The seed data provides:
- ✓ Verified providers across India
- ✓ Multiple states and cities covered
- ✓ Contact information for each provider
- ✓ Specializations and languages
- ✓ Organization types and verification status

## Maintenance

To keep the seed data current:

1. **Regular Updates**: Review and update provider information quarterly
2. **Verification**: Verify contact information is still valid
3. **New Providers**: Add new legal aid organizations as they become available
4. **Deprecated Providers**: Remove or mark inactive providers

## Troubleshooting

### PostgreSQL Connection Error
```
Error: connection to server at "localhost" failed
```
**Solution**: Ensure PostgreSQL is running and connection details in `.env` are correct

### File Not Found Error
```
Error: Seed data file not found
```
**Solution**: Ensure `legal_aid_providers_seed_data.json` exists in the backend directory

### JSON Decode Error
```
Error: Invalid JSON in seed data file
```
**Solution**: Validate JSON syntax using a JSON validator

### Validation Errors
```
Provider X: Invalid organization type
```
**Solution**: Check that organization_type matches one of the valid types

## Related Files

- `models/legal_aid_provider.py` - Database model definition
- `routers/legal_aid.py` - API endpoints (to be implemented in Task 13.3)
- `.kiro/specs/nyaya-mitra/tasks.md` - Task 13.1 specification
- `.kiro/specs/nyaya-mitra/requirements.md` - Requirement 5.5

## Support

For issues or questions about the seeding system:
1. Check test output for validation errors
2. Review error messages from seeding script
3. Verify seed data format matches schema
4. Ensure database connection is working
