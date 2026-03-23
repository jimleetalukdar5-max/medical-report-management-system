#  medical-report-management-system

## Features
- User login with OTP verification
- Secure file upload (AES encryption)
- Role-based access (Doctor/Patient)
- Audit logging system

## Tech Stack
- Python (Flask)
- MySQL
- Cryptography (AES)

## Setup
1. Create .env file
2. Install dependencies:
   pip install -r requirements.txt
3. Run:
   python app.py

## Security Features
1. Passwords are securely hashed
2. OTP-based login with expiry and attempt limits
3. AES encryption used for file storage
4. Sensitive data managed using environment variables
