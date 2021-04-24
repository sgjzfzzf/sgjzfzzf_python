# Rabin密码系统的实现
# 作者：刘津榤
# 时间：2021.4.24


import sympy as sym


class RabinModel:
    # 利用了sympy库的数论模块Rabin密码系统的实现，目前只能实现ASCII字符的加密解密
    # 定义标识符，因为最终解码的时候会生成四个可能的答案，于是希望通过在加密时为每个字符串片段加上标识符以便于在解密的结果中帮助确定唯一正确的答案
    identifier = '00'

    def __init__(self):
        # 随机生成初始数值
        self.p = sym.randprime(pow(2, 28), pow(2, 29)-1)  # 随机生成指定范围内的素数
        self.q = sym.randprime(pow(2, 28), pow(2, 29)-1)
        while self.p % 4 != 3:  # 反复生成确保素数的形式为4k+3型
            self.p = sym.randprime(pow(2, 28), pow(2, 29)-1)
        while self.q % 4 != 3:
            self.q = sym.randprime(pow(2, 28), pow(2, 29)-1)
        self.n = self.p*self.q

    def encode(self, message: str):
        # 加密函数，传入的参数为原文字符串
        messages = list()
        ciphertexts = list()
        for i in range(0, len(message), 5):  # 对字符串做切割，形成五个一组的字符串数组
            messages.append(message[i:i+5])
        for eachMessage in messages:
            ciphertext = ""
            for ch in eachMessage:
                # 生成字符串片段对应的二进制码，注意统一调整每个字符对应二进制的长度为两位
                ciphertext += hex(ord(ch))[2:].rjust(2, '0')
            ciphertext += self.identifier  # 加上标识符
            ciphertexts.append(pow(int(ciphertext, 16), 2, self.n))
        return ciphertexts

    def getKey(self):
        # 输出密钥用函数
        return self.p, self.q

    def decode(self, ciphertexts: list, p, q):
        # 解密函数，传入参数为加密函数生成的密文，密钥p、q
        n = p*q
        plaintext = ""
        for ciphertext in ciphertexts:  # 对每一小段密文进行解密后拼接成明文
            rootp = pow(ciphertext, (p+1)//4, p)
            rootq = pow(ciphertext, (q+1)//4, q)
            inversep = sym.mod_inverse(p, q)
            inverseq = sym.mod_inverse(q, p)
            m1 = (rootq*p*inversep+rootp*q*inverseq) % n
            m2 = n-m1
            m3 = (rootq*p*inversep-rootp*q*inverseq) % n
            m4 = n-m3
            for m in m1, m2, m3, m4:
                m = hex(m)[2:]
                if m[-2:] == self.identifier:  # 找出四个可能答案中正确位置含有标识符的字符串并拼接进输出的明文中
                    for num in range(0, len(m)-2, 2):
                        plaintext += chr(int(m[num:num+2], 16))
        return plaintext


model = RabinModel()
p, q = model.getKey()
ciphertext = model.encode(
    "m = Communication Skill + Mathematical Fundation of Information security + 201202001 + Student ID + 000001")
print(model.decode(ciphertext, p, q))
