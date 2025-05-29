from cryptography.fernet import Fernet
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def generate_key(password):
    # Generate a key from password using PBKDF2
    salt = b'static_salt_for_db_doc'  # Must match encryption salt
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key

def decrypt_file(input_file, output_file, password):
    # Generate decryption key from password
    key = generate_key(password)
    f = Fernet(key)
    
    # Read the encrypted file
    with open(input_file, 'rb') as file:
        encrypted_data = file.read()
    
    # Decrypt the data
    decrypted_data = f.decrypt(encrypted_data)
    
    # Write the decrypted data
    with open(output_file, 'wb') as file:
        file.write(decrypted_data)
