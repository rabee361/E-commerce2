from cryptography.fernet import Fernet
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os

def generate_key(password):
    # Generate a key from password using PBKDF2
    salt = b'static_salt_for_db_doc'  # In production, use a random salt and store it
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key

def encrypt_file(input_file, output_file, password):
    # Generate encryption key from password
    key = generate_key(password)
    f = Fernet(key)
    
    # Read the input file
    with open(input_file, 'rb') as file:
        file_data = file.read()
    
    # Encrypt the data
    encrypted_data = f.encrypt(file_data)
    
    # Write the encrypted data
    with open(output_file, 'wb') as file:
        file.write(encrypted_data)

def main():
    input_file = 'db_doc.md'
    output_file = 'db_doc.md.encrypted'
    
    # Get password from user
    password = input("Enter encryption password: ")
    
    try:
        encrypt_file(input_file, output_file, password)
        print(f"File encrypted successfully. Encrypted file saved as {output_file}")
    except Exception as e:
        print(f"Error encrypting file: {e}")

if __name__ == "__main__":
    main() 