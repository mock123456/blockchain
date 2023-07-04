import hashlib
import json
import typing
import time
from blockchain_basic.database import length_block, show_all, upload_block, create_collection, drop_all, upload_many


# 这个文件包含两个类
# Node类负责发起交易,写入账本
# Blockchain类记录链上的节点和节点数量,同时拥有共识算法resolve_conflict,以最长链为基准更新各节点的账本


class Node:

    def __init__(self, name: str, failure: int):
        # 节点的名称,创建和打开collection的依据
        self.name = name
        # 节点的故障率.例如:当failure为3时,故障率是1/3
        self.failure = failure
        # 存储最近一次发起的交易,如果交易不成功,那么清空数据
        self.current_transaction = []
        # 存储最近一次的区块,初始化时为创世块,再次初始化时,会返回该节点账本中的最后一个区块
        self.last_block = create_collection(name)

    def new_transaction(self, sender: str, recipient: str, amount: int):
        """添加新的交易,返回准备提交区块的index"""
        print(f"name:{self.name}")
        print(f"current_transaction:{self.current_transaction}")
        transaction = {
            'sender': sender,
            "recipient": recipient,
            "amount": amount,
        }
        # 添加这笔交易到当前的交易
        print("正在创建交易")
        self.current_transaction.append(transaction)

    def new_block(self):
        """向本节点的账本添加一个区块"""
        # print(self.last_block)
        # print(type(self.last_block))
        block = {
            "index": length_block(self.name),
            "timestamp": time.time(),
            "transaction": self.current_transaction,
            "proof": self.proof_of_work,
            "previous_hash": self.hash(self.last_block),
        }
        # 保存最新添加的区块
        self.last_block = block.copy()
        # 上传区块到账本
        upload_block(self.name, block)
        # 清空当前的交易
        self.current_transaction.clear()

    # @staticmethod(静态方法),定义在类里的函数，并没有非要定义的必要
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

    # 加了这个之后,就可以修饰属性.例如:可以直接使用Node.hash调用.详细请看博客http://t.csdn.cn/uqWoq.
    # 把一个方法变成属性调用，起到既能检查属性，还能用属性的方式来访问该属性的作用

    # 验证计算值是否符合要求
    def valid_proof(last_proof: int, proof: int) -> bool:
        """工作量证明计算,验证计算结果是否是2个0开头"""
        # f'{1}{2}' = 12,此处直接连接了两个数字.encode将str编码成二进制的Bytes类型
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        if guess_hash[0:2] == "00":
            return True
        else:
            return False

    @property
    def proof_of_work(self) -> int:
        """工作量计算,计算一个符合要求的哈希值"""
        proof = 0
        last_proof = self.last_block['proof']
        # is和==的区别,请看博客http://t.csdn.cn/xWxsp.is要内存地址一致
        while Node.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    # # 验证计算值是否符合要求
    # def valid_proof(self, last_proof: int, proof: int) -> bool:
    #     """工作量证明计算,验证计算结果是否是2个0开头"""
    #     # f'{1}{2}' = 12,此处直接连接了两个数字.encode将str编码成二进制的Bytes类型
    #     guess = f'{last_proof}{proof}'.encode()
    #     guess_hash = hashlib.sha256(guess).hexdigest()
    #     if guess_hash[0:2] == "00":
    #         return True
    #     else:
    #         return False


class Blockchain:
    """继承了Node的部分方法和变量"""

    def __init__(self, num: int, failure: int):
        """init方法会自动创建指定数量的节点,failure为故障率,方便后期进行pbft算法的实验.init方法还能自动创建对应名称的数据库,生成创世块."""
        self.nodes = set()
        # 需要注册节点数量
        self.num = num
        # 节点的故障率
        self.failure = failure

    def resolve_conflict(self):
        """共识算法:寻找最长的,且有效的链条,以它为主"""
        # 获取所有的节点
        neighbors = self.nodes
        # 获取当前链条的长度,默认使用node0账本
        max_length = 0
        # 暂时存储链条
        new_chain = None
        temp = None
        # 遍历所有的节点
        for node in neighbors:
            print(f"当前正在查验{node}节点")
            # 验证链是否有效,同时找到拥有最长链的节点
            if length_block(node) > max_length and self.valid_chain(show_all(node)):
                max_length = length_block(node)
                new_chain = show_all(node)
                temp = node
        print(f"max_length:{max_length}")
        print(f"new_chain:{new_chain}")
        print(f"temp:{temp}")
        if new_chain:
            # 删除其他节点的所有账本,替换成new_chain
            for node in neighbors:
                if node != temp:
                    drop_all(node)
                    upload_many(node, new_chain)
        print("账本已经全部更新完毕")

    def valid_chain(self, chain: typing.List[typing.Dict[str, typing.Any]]) -> bool:
        """验证链是否最长,并且有效"""
        # 从创世块开始校验
        last_block = chain[0]
        current_index = 1
        while current_index < len(chain):
            block = chain[current_index]
            # 打印出上个和当前的block
            print(f'last_block:{last_block}')
            print(f'block:{block}')
            print("\n--------------\n")
            # 如果当前哈希值和计算出来的哈希值不同,则是无效链
            if block['previous_hash'] != Node.hash(last_block):
                print('当前哈希值和计算出来的哈希值不同,是无效链')
                return True
            # 检查工作量证明是否符合要求0
            if not Node.valid_proof(last_proof=last_block['proof'], proof=block['proof']):
                print('工作量证明失败')
                return False
            last_block = block
            current_index += 1
        return True


# # 以下为测试代码
#
# # 创建一个10个节点的区块链网络
# blockchain = Blockchain(10, 0)
# # 根据实验的要求,设置需要的节点数量和故障率,初始化节点
# nodes = {}
# for i in range(10):
#     nodes["node" + str(i)] = Node("node" + str(i), failure=0)
#     blockchain.nodes.add("node" + str(i))
# # 此时已经创建了10个节点了,并且在数据库中生成了创世块,接下来测试一下交易和生成区块
#
# # 为node0生成交易,此时node0会工作量证明并且生成交易和区块,然后验证之前的区块是否被篡改.都成功后，写入数据库中
# nodes["node0"].new_transaction("Alice", "Bob", 5)
# nodes["node0"].new_transaction("Bob", "Mike", 5)
# nodes["node0"].new_block()
# blockchain.resolve_conflict()
