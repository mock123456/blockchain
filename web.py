import typing

import flask
from argparse import ArgumentParser
from blockchain_basic import blockchain

# 使用flask部署服务器,__name为根路径,用来获取app的文件等等,app为实例化的flask对象,这个前端做的是有问题的,并没有和实际的数据产生交互,甚至无法调用blockchain.py里头的函数
app = flask.Flask(__name__)
# 创建一个blockchain实例,第一次测试Web用
my_channel = blockchain.BlockChain()

# last_block = my_channel.last_block
# last_proof = last_block['proof']
# proof = my_channel.proof_of_work(last_proof)
# my_channel.new_transaction(
#     sender="0",
#     recipient="node_identifier",
#     amount=1
# )
# block = my_channel.new_block(proof, None)
# print(my_channel.chain)


# 测试flask代码
@app.route('/')
def test():
    return "</p>hello world<p>"


# 视图函数,浏览器输入localhost:5000/transactions/new
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = flask.request.get_json()
    required = ['sender', 'recipient', 'amount']
    # 遍历后有部分不在
    if not all(k in values for k in required):
        return "缺少参数", 400
    index = my_channel.new_transaction(values['sender'], values['recipient'], values['amount'])
    response = {'message': f'交易会被添加到块{index}'}
    return flask.jsonify(response), 201


# 这个函数里头有很多的问题
@app.route('/mine', methods=['GET'])
def mine():
    last_block = my_channel.last_block
    last_proof = last_block['proof']
    proof = my_channel.proof_of_work(last_proof)
    # 发送者为0,表示是新挖出的矿,为矿工提供奖励
    # my_channel.new_transaction(
    #     sender="0",
    #     recipient="node_identifier",
    #     amount=1
    # )
    # 生成一个新块
    block = my_channel.new_block(proof, None)
    response = {
        'message': "打包成功,新区块已形成",
        'index': block['index'],
        'transaction': block['transaction'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']
    }
    return flask.jsonify(response), 200


# 获取链
@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        "chain": my_channel.chain,
        'length': len(my_channel.chain)
    }
    return flask.jsonify(response), 201


# 注册节点
@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = flask.request.get_json()
    nodes = values.get('nodes')
    if nodes is None:
        return "Error:请提供一个符合规则的节点", 400

    for node in nodes:
        my_channel.register_node(node)
    response = {
        'message': "新节点已被添加",
        'total_nodes': list(my_channel.nodes)
    }
    return flask.jsonify(response), 200


# 共识算法
@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = my_channel.resolve_conflict()
    if replaced:
        response = {
            'message': "当前链不符合规则,已被替换",
            'new_chain': my_channel.chain
        }
    else:
        response = {
            'message': "当前链符合规则",
            'chain': my_channel.chain
        }
    return flask.jsonify(response), 200


# 节点注册接口
@app.route('/nodes/register', methods=['POST'])
def registerNode():
    values = flask.request.get_json()
    nodes = values.get('nodes')
    if nodes is None:
        return "Error:请提供一个符合规则的节点", 400
    for node in nodes:
        my_channel.register_node(node)

    response = {
        'message': "新节点已经被添加",
        'total_nodes': list(my_channel.nodes)
    }
    return flask.jsonify(response), 200


if __name__ == '__main__':
    # 通过解析命令行,获取端口号
    parser = ArgumentParser()
    parser.add_argument('-p',
                        '--port',
                        default=5000,
                        type=int,
                        help='port to listen on')
    # 解析命令行的参数,获取port
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port, debug=True)
