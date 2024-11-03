import hashlib

# Input string
input_string = "Duyquang22"

# Create SHA-256 hash
sha256_hash = hashlib.sha256(input_string.encode()).hexdigest()

print("SHA-256 hash:", sha256_hash)
