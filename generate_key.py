from cryptography.fernet import Fernet

# Function to generate and save an encryption key
def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)
    print("Encryption key generated and saved to 'secret.key'.")

# Main function
def main():
    # Generate the key
    generate_key()

if __name__ == "__main__":
    main()
