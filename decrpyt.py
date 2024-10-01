import subprocess
import json
import pandas as pd
from cryptography.fernet import Fernet

# Function to generate an encryption key (uncomment to run once)
def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)

# Function to load the encryption key
def load_key():
    return open("secret.key", "rb").read()

# Function to encrypt the API key
def encrypt_api_key(api_key):
    f = Fernet(load_key())
    encrypted_key = f.encrypt(api_key.encode())
    return encrypted_key

# Function to decrypt the API key
def decrypt_api_key(encrypted_key):
    try:
        f = Fernet(load_key())
        decrypted_key = f.decrypt(encrypted_key.encode()).decode()
        return decrypted_key
    except Exception as e:
        print(f"Failed to decrypt API key: {e}")
        raise  # Re-raise the exception for higher-level handling


# Function to execute curl command and get data
def execute_curl_and_get_data(curl_command):
    print(f"Executing curl command: {curl_command}")  # Print the curl command for debugging
    
    # Execute the curl command directly in the shell
    result = subprocess.run(curl_command, shell=True, capture_output=True, text=True)
    
    # Print the response for debugging
    print(f"Curl response: {result.stdout[:200]}...")  # Print the first 200 characters of the response
    
    # Check for errors
    if result.returncode != 0:
        print(f"Error executing command: {result.stderr}")
        return None
    
    # Return the full response (assuming it's JSON)
    return result.stdout

# Function to parse JSON response and write to CSV
def parse_and_write_to_csv(json_data, output_file):
    if json_data:
        try:
            data = json.loads(json_data)
            print(f"Full JSON response: {json.dumps(data, indent=2)}")  # Pretty print the JSON response

            # Check for keys and parse accordingly
            if 'values' in data:
                value_list = []

                # Extract values based on your JSON structure
                for item in data['values']:
                    value = item['value']
                    value_list.append({
                        'Rank': value[0],
                        'Flag': value[1],
                        'Team': value[2],
                        'PCT': value[3]
                    })

                # Create a DataFrame and write to CSV
                df = pd.DataFrame(value_list)
                df.to_csv(output_file, index=False)
                print(f"Data written to {output_file}")
            else:
                print("'values' key not found in JSON response.")
        except json.JSONDecodeError:
            print("Failed to decode JSON response.")
    else:
        print("No data to parse.")

# Main function
# Main function
def main():
    # Load the commands from the input_curl.txt file
    with open("input_curl.txt", "r") as file:
        commands = file.readlines()

    # Process each command
    for i, command in enumerate(commands):
        command = command.strip()
        print(f"Processing command {i + 1}: {command}")

        try:
            # Check if the command contains the API key
            if 'x-rapidapi-key: ' in command:
                # Use regex to extract the API key
                import re
                match = re.search(r'x-rapidapi-key:\s*([^"\s]+)', command)
                if match:
                    encrypted_key = match.group(1)

                    # Decrypt the API key
                    api_key = decrypt_api_key(encrypted_key)  # Ensure this function is defined
                    print("Decrypted API Key:", api_key)  # Debugging, remove if not needed

                    # Replace the API key in the command with the decrypted key
                    command = command.replace(encrypted_key, api_key)

                    # Execute the curl command
                    json_response = execute_curl_and_get_data(command)
                    if json_response:
                        output_file = f"output_{i + 1}.csv"
                        parse_and_write_to_csv(json_response, output_file)
                    else:
                        print(f"No valid response for command {i + 1}.")
                else:
                    print("API key not found in command.")
            else:
                print("API key not found in command.")

        except Exception as e:
            print(f"An error occurred while processing command {i + 1}: {str(e)}")
            # Optionally log the command causing the error
            print(f"Command that caused the error: {command}")

if __name__ == "__main__":
    main()
