import base64
from cryptography.fernet import Fernet

# Function to generate a new encryption key (run this once to create a key)
def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)
    print("Key generated and saved to 'secret.key'")

# Function to load the encryption key
def load_key():
    return open("secret.key", "rb").read()

# Function to encrypt the curl command
def encrypt_command(command):
    f = Fernet(load_key())
    # Encrypt the command
    encrypted_command = f.encrypt(command.encode())
    # Encode the encrypted command in base64 to make it safe for storage
    return base64.urlsafe_b64encode(encrypted_command).decode()

# Function to decrypt the curl command
def decrypt_command(encrypted_command):
    f = Fernet(load_key())
    # Decode from base64
    decoded_command = base64.urlsafe_b64decode(encrypted_command)
    # Decrypt the command
    return f.decrypt(decoded_command).decode()

# Example usage
if __name__ == "__main__":
    # Uncomment to generate a key the first time you run this script
    # generate_key()

    # Example curl command
    curl_command = 'curl -X GET "https://api.example.com/data" -H "x-api-key: your_api_key"'

    # Encrypt the curl command
    encrypted_command = encrypt_command(curl_command)
    print(f"Encrypted command: {encrypted_command}")

    # Decrypt the command
    decrypted_command = decrypt_command(encrypted_command)
    print(f"Decrypted command: {decrypted_command}")
