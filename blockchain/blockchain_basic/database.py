import time
import typing

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# 注意这里要替换掉<password>为你的密码
uri = "mongodb+srv://mock:kx135549@cluster0.ggh2wmr.mongodb.net/?retryWrites=true&w=majority"

# 创建一个客户端以连接上mongoDB云服务器
client = MongoClient(uri, server_api=ServerApi('1'))
# 打开并创建blockChain数据库,这个数据库用来存储各节点的账本
db = client["blockChain"]
db_list = client.list_database_names()


# 打开并创建organizations数据库,这个数据库内只有一张collection表,用来保存节点的信息.

def create_collection(node: str) -> dict:
    """用于节点的初始化:创建节点的账本,添加创世块到账本"""
    # 首先查看账本是否存在,如果不存在,那么创建数据库,否则pass
    if node in db.list_collection_names():
        last_block = show_all(node)[-1]
    else:
        # 创世块
        block = {
            "index": 0,
            "timestamp": time.time(),
            "transaction": [],
            "proof": 100,
            "previous_hash": "1"
        }
        # python只会复制变量的地址,因此这样会产生问题,此时打印地址,可以发现都返回True
        # last_block = block
        # print(id(block)==id(last_block))

        # 因此可以进行浅拷贝,详细见http://t.csdn.cn/zj4yy
        last_block = block.copy()
        print(f"正在为{node}创建collection")
        # 创建账本
        db.create_collection(node)
        # 添加创世块到节点的账本里
        upload_block(node, block)
    # 不管如何,返回最后一个区块
    return last_block


def show_all(node: str) -> list:
    """导出该节点存储的区块链,返回一个列表,该列表内存储着链"""
    # 打开对应节点的collection
    collection = db[node]
    # 创建一个列表,把数据读到里头去
    output = []
    # 重新构建一个json格式,忽略掉mongoDB自动添加的_id
    for data in collection.find():
        current_block = {
            "index": data["index"],
            "timestamp": data["timestamp"],
            "transaction": data["transaction"],
            "proof": data["proof"],
            "previous_hash": data["previous_hash"]
        }
        output.append(current_block)
    return output


def upload_block(node: str, block: dict[str, any]):
    """向节点的账本上传区块,会返回一个插入后的实例,包括mongoDB的_id"""
    # 打开节点的账本
    collection = db[node]
    # 插入数据
    collection.insert_one(block)


def length_block(node: str) -> int:
    """查看指定节点的链的长度"""
    # 打开指定节点的账本
    collection = db[node]
    # 计算链的长度
    length = collection.count_documents({})
    return length


def drop_all(node: str) -> None:
    """删除该节点账本上的所有信息"""
    # 打开node的账本
    collection = db[node]
    # 传参为空,即删除该账本的所有信息
    collection.delete_many({})
    print(f'{node}的账本已经清除!')


def upload_many(node: str, data: list) -> None:
    """上传一整条链"""
    # 打开node的账本
    collection = db[node]
    # 按照顺序一次上传多个json数据
    collection.insert_many(data, ordered=True)
    print(f'{node}的账本已经被更新')
