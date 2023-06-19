import hashlib
import json
import time
from urllib.parse import urlparse
import requests


# 这是一个简单的python模拟区块链的demo,区块结构如下
# {
#     "index":0, // 块序号
#     "timestamp":"",// 时间戳
#     "transactions":""[ // 交易信息
#         {
#             "sender":"",
#             "recipient":"",
#             "amount":5,
#         }
#     ],
#     "proof":"", // 工作量证明
#     "previous_hash":"",// 前区块的哈希值
# }
# 这么多函数,割裂开了,每个模块的意义是什么呢
# 首先得创建交易,然后再创建区块

class BlockChain:
    """类:区块链"""


    def __init__(self):
        # 设置成集合,避免重复
        self.nodes = set()
        # 存链
        self.chain = []
        # 交易实体（当前的交易信息）
        self.current_transaction = []
        # 生成创世块
        self.new_block(proof=100, previous_hash='1')

    def new_block(self, proof: int, previous_hash=None):
        """新建区块"""
        block = {
            # len()获取长度,然后加一
            "index": len(self.chain) + 1,
            # 此处csdn有错误,应为time.time()获取时间戳
            "timestamp": time.time(),
            "transaction": self.current_transaction,
            "proof": proof,
            "previous_hash": previous_hash or hash(self.hash(self.last_block)),
        }
        # 重置当前交易
        self.current_transaction = []
        # 将区块上链
        self.chain.append(block)
        # 返回一个block
        return block

    def new_transaction(self, sender: str, recipient: str, amount: int) -> int:
        """添加新的交易"""
        self.current_transaction.append({
            'sender': sender,
            "recipient": recipient,
            "amount": amount,
        })
        return self.last_block['index'] + 1

    # 加了这个之后,就可以修饰属性,详细请看博客http://t.csdn.cn/uqWoq
    @staticmethod
    def hash(block: dict[str, any]) -> str:
        """计算哈希值,返回哈希后的摘要信息

        Args:
            block (Dict[str, Any]): 传入一个块

        Returns:
            str: 摘要信息
        """
        # 不懂这里,已经有dumps,为啥还要加一个encode():dump是进行一个排序,避免每次的block字典顺序不一样,再进行一个编码
        block_string = json.dumps(block, sort_keys=True).encode()
        # 返回哈希值的十六进制数
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        """返回最后一个区块"""
        return self.chain[-1]

    def proof_of_work(self, last_proof: int) -> int:
        """工作量计算,计算一个符合要求的哈希值"""

        proof = 0
        # is和==的区别,请看博客http://t.csdn.cn/xWxsp.is要内存地址一致
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
            # print(proof),第一次测试用
        return proof

    # 验证计算值是否符合要求
    def valid_proof(self, last_proof: int, proof: int) -> bool:
        """工作量证明计算,验证计算结果是否是2个0开头"""
        # f'{1}{2}' = 12,此处直接连接了两个数字.encode将str编码成二进制的Bytes类型
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        # print(guess_hash)打印哈希值,第一次测试用
        if guess_hash[0:2] == "00":
            return True
        else:
            return False

    # 节点注册
    def register_node(self, address: str) -> None:
        """添加一个新节点到节点集中"""
        # 解析url
        parsed_url = urlparse(address)
        # 获取域名netloc.
        self.nodes.add(parsed_url.netloc)

    def resolve_conflict(self) -> bool:
        """共识算法:寻找最长的,且有效的链条,以它为主"""
        # 获取所有的节点
        neighbors = self.nodes
        # 获取当前链条的长度
        max_length = len(self.chain)
        # 暂时存储链条
        new_chain = None
        # 遍历所有的节点
        for node in neighbors:
            response = requests.get(f"http://{node}/chain")
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                # 用长的链条覆盖掉短的
                if length > max_length:
                    max_length = length
                    new_chain = chain

        # 如果找到了更长的链条
        if new_chain:
            self.chain = new_chain
            return True
        else:
            return False

# #第二次测试用,postman
# app = flask.Flask(__name__)
# if __name__ == '__main__':
#     app.run(host='0.0.0.0',port=5000)


# testpow = BlockChain()       第一次测试用
# testpow.proof_of_work(100)    第一次测试用
