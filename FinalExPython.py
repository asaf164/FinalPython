#FinalPythonExercise - Asaf Biran 10.17.25
#To encrypt type encrypt and then the text you want to encrypt
# the encrypted message will be found in: encrypted_msg.txt
#to  decrypt type the command decrypt and the last encrypted message will be revealed


import sys
import logging

#logging setup
logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

try:
    cmd = sys.argv[1]
    log.info("received command: %s", cmd)
except IndexError:
    log.error("did not get encrypt/decrypt cmd. exiting..")
    print("did not get encrypt/decrypt cmd.exiting..")
    exit(-1)


decrypt_table = {
    56: "A", 57: "B", 58: "C", 59: "D", 40: "E", 41: "F", 42: "G", 43: "H",
    44: "I", 45: "J", 46: "K", 47: "L", 48: "M", 49: "N", 60: "O", 61: "P",
    62: "Q", 63: "R", 64: "S", 65: "T", 66: "U", 67: "V", 68: "W", 69: "X",
    10: "Y", 11: "Z", 12: "a", 13: "b", 14: "c", 15: "d", 16: "e", 17: "f",
    18: "g", 19: "h", 30: "i", 31: "j", 32: "k", 33: "l", 34: "m", 35: "n",
    36: "o", 37: "p", 38: "q", 39: "r", 90: "s", 91: "t", 92: "u", 93: "v",
    94: "w", 95: "x", 96: "y", 97: "z", 98: " ", 99: ",", 100: ".", 101: "'",
    102: "!", 103: "-"
    }

encrypt_table = {}

for k, v in decrypt_table.items():
    encrypt_table[v] = k              #loop to flip the vars for the encryption table

def encrypt(text):
    return ",".join(str(encrypt_table[ch]) for ch in text)  #converts text into a list of encrypted nums

def decrypt(numbers):
    nums = [int(x) for x in numbers.split(",")]
    return "".join(decrypt_table[num] for num in nums)  #turns the numbers into text

assert encrypt("hello world") == "19,16,33,33,36,98,94,36,39,33,15", "encryption failed"
assert decrypt("19,16,33,33,36,98,94,36,39,33,15") == "hello world", "decryption failed"


if cmd == "encrypt":
    try:
        text = " ".join(sys.argv[2:])
        log.info("text to encrypt: %s", text)
        if not text.strip():
            log.error("no text provided to encrypt")
            print("Error: no text provided to encrypt")
        else:
            encrypted = encrypt(text)
            with open("encrypted_msg.txt", "w") as f:   #opens the file and puts it on write mode
                f.write(encrypted)
            log.info("message encrypted and saved to file")
            print("Message encrypted and saved to encrypted_msg.txt")
    except Exception as e:
        log.error("encryption failed: %s", e)
        print("Encryption failed:", e)   #incase of a usage of a letter not in the bracket

elif cmd == "decrypt":
    try:
        with open("encrypted_msg.txt", "r") as f:   #opens the file and puts it in read mode
            content = f.read()   #saves the content of the file into 'content'
        message = decrypt(content)   #decrypts the message
        log.info("decrypted message: %s", message)
        print("Decrypted message:", message)
    except FileNotFoundError:
        log.error("file not found")
        print("File not found")
    except ValueError as e:
        log.error("decryption error: %s", e)
        print("Error:", e)


print ("cmd:", cmd)  #shows the user what command he used


    






