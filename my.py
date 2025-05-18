import random
import math
from sympy import isprime
import time

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

    # 生成素数
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
        print(f"p: {p}  q: {q}")
        while q == p:
            q = self.generate_prime(self.key_length)

        n = p * q
        phi = (p - 1) * (q - 1)

        # 选择一个与 φ(n) 即 phi 互质的整数 e 作为公钥
        e = random.randint(2, phi - 1)
        while self.gcd(e, phi) != 1:
            e = random.randint(2, phi - 1)
        print(f"e: {e}")

        # 计算 e 在模 φ(n) 下的模逆 d 作为私钥
        d = self.mod_inverse(e, phi)
        print(f"d: {p}")

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
    
# 基于 Pollard's Rho 算法的因数分解函数，用于分解一个大整数 n 的因数
def pollards_rho(n):
    if n % 2 == 0:
        return 2
    if n % 3 == 0:
        return 3
    if n % 5 == 0:
        return 5
    
    while True:
        c = random.randint(1, n-1)
        f = lambda x: (pow(x,2,n) + c) % n
        x, y, d = 2, 2, 1
        while d == 1:
            x = f(x)
            y = f(f(y))
            d = math.gcd(abs(x-y), n)
        if d != n:
            return d
# 递归，用于将一个大整数n完全分解为素因数的列表
def factorize(n):
    if n == 1:
        return []
    if isprime(n):
        return [n]
    d = pollards_rho(n)
    return factorize(d) + factorize(n//d)

def main():
    key_lengths = [8, 12, 20, 32, 40]  
    results = []

    for key_length in key_lengths:
        print(f"\n生成 {key_length} 位 的密钥：")
        rsa = RSA(key_length)
        public_key, private_key = rsa.generate_keys()
        e, n = public_key
        d, _ = private_key

        # 生成一个简单明文
        m = random.randint(2, n-1)
        print(f"明文: {m}")
        
        # 加密
        c = rsa.encrypt(m, public_key)
        print(f"加密得到的密文: {c}")
        
        # 解密
        decrypted_m = rsa.decrypt(c, private_key)
        print(f"解密得到的明文: {decrypted_m}")

        # Crack
        print("开始破解：")
        print(f"n = {n}")
        start_time = time.time()
        factors = factorize(n)
        end_time = time.time()
        crack_time = end_time - start_time
        print(f"破解得到的p、q: {factors}")
        print(f"破解时间: {crack_time:.6f} 秒")
        
        results.append((key_length, crack_time))


if __name__ == "__main__":
    main()