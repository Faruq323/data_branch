# Decoding the Base64 command
decoded_command = base64.b64decode(encoded_command).decode('utf-8')

print("\nDecoded Command:")
print(decoded_command)
