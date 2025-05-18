import random
import hashlib
import time
from sympy import isprime

class RSA:
    def __init__(self, key_length):
        self.key_length = key_length
        self.public_key = None
        self.private_key = None

    def gcd(self, a, b):
        while b != 0:
            a, b = b, a % b
        return a
    # 模逆（e*d=1(mod phi) ）
    def mod_inverse(self, a, m):
        m0 = m
        y = 0
        x = 1
        if m == 1           :
            return 0
        while a > 1:    
            q = a // m
            m, a = a % m, m
            x, y = y, x - q * y
        if x < 0:
            x += m0
        return x

    # 生成素数p、q
    def generate_prime(self, bits):
        while True:
            p = random.getrandbits(bits)
            p |= (1 << (bits - 1)) | 1  
            if isprime(p):
                return p

    def generate_keys(self):
        # 生成指定位数的两个素数p、q
        p = self.generate_prime(self.key_length)
        q = self.generate_prime(self.key_length)
        while q == p:
            q = self.generate_prime(self.key_length)

        n = p * q
        phi = (p - 1) * (q - 1)

        # 选择一个与 φ(n) 即 phi 互质的整数 e 作为公钥
        e = random.randint(2, phi - 1)
        while self.gcd(e, phi) != 1:
            e = random.randint(2, phi - 1)

        # 计算 e 在模 φ(n) 下的模逆 d 作为私钥
        d = self.mod_inverse(e, phi)

        self.public_key = (e, n)
        self.private_key = (d, n)
        return (e, n), (d, n)

    # 加密
    def encrypt(self, plaintext, public_key):
        e, n = public_key
        ciphertext = pow(plaintext, e, n)
        return ciphertext

    #解密
    def decrypt(self, ciphertext, private_key):
        d, n = private_key
        plaintext = pow(ciphertext, d, n)
        return plaintext
    
    # 签名
    def sign(self, message_bytes, private_key):
        hash_value = int.from_bytes(hashlib.sha256(message_bytes).digest(), byteorder='big')
        signature = self.encrypt(hash_value, private_key) 
        return signature

    # 验证
    def verify(self, message_bytes, signature, public_key):
        hash_from_signature = self.decrypt(signature, public_key)  
        actual_hash = int.from_bytes(hashlib.sha256(message_bytes).digest(), byteorder='big')
        return hash_from_signature == actual_hash



def main():
    key_lengths = [128, 256, 512,1024]
    message = b"This is a message for RSA digital signature performance test."
    print("密钥长度 | 密钥生成时间 | 签名时长 | 验证时长 | 验证结果")
    print("--------------------------------------------------")
    
    for key_length in key_lengths:
        rsa = RSA(key_length)

        start = time.time()
        public_key, private_key = rsa.generate_keys()
        keygen_time = time.time() - start

        start = time.time()
        signature = rsa.sign(message, private_key)
        sign_time = time.time() - start

        start = time.time()
        result = rsa.verify(message, signature, public_key)
        verify_time = time.time() - start

        print(f"{key_length:8} | {keygen_time:12.6f} | {sign_time:8.6f} | {verify_time:9.6f} | {result:1}")


if __name__ == "__main__":
    main()
