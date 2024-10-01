import base64

# Your curl command as a string
curl_command = 'curl -X POST https://api.example.com/data -H "Authorization: Bearer TOKEN" -d \'{"key":"value"}\''

# Encode the command to bytes, then to Base64
encoded_command = base64.b64encode(curl_command.encode('utf-8')).decode('utf-8')

print("Encoded Base64 Command:")
print(encoded_command)



# Decoding the Base64 command
decoded_command = base64.b64decode(encoded_command).decode('utf-8')

print("\nDecoded Command:")
print(decoded_command)
