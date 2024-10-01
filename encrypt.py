from cryptography.fernet import Fernet

# Function to load the encryption key
def load_key():
    return open("secret.key", "rb").read()

# Function to encrypt the API key
def encrypt_api_key(api_key):
    f = Fernet(load_key())
    encrypted_key = f.encrypt(api_key.encode())
    return encrypted_key

# Main function
def main():
    # Your actual API key
    api_key = "Your api key"  # Replace this with your actual API key

    # Encrypt the API key
    encrypted_key = encrypt_api_key(api_key)
    print(f"Encrypted API Key: {encrypted_key.decode()}")

if __name__ == "__main__":
    main()
#Encrypted API Key: gAAAAABm-_VRbBq0TlrY_oBoWmxfEIlHrqDi5sM1ta3xrqmwWcVHJ1Gnr3oM-3dFBZpx1vEvEI1_M8zxj4LHFVmav5mBF5pDa-6tdOjH7T6XLU8hVcc8bdrK1a4a0_gtssgN8RHJnJILx4z1U8JTDU1il8aLqFD53Q==
