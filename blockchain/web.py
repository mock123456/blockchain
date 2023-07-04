import flask
from argparse import ArgumentParser
from blockchain_basic.blockchain import Blockchain, Node
from blockchain_basic.database import show_all, length_block

# 使用flask部署服务器,__name为根路径,用来获取app的文件等等,app为实例化的flask对象,这个前端做的是有问题的,并没有和实际的数据产生交互,甚至无法调用blockchain.py里头的函数
app = flask.Flask(__name__)
# 初始化10个节点的区块链网络
blockchain = Blockchain(10, 0)
nodes = {}
for i in range(10):
    nodes["node" + str(i)] = Node("node" + str(i), failure=0)
    blockchain.nodes.add("node" + str(i))


# 测试flask代码
@app.route('/', methods=['GET'])
def test():
    print(nodes["node1"].last_block)
    return "</p>hello world<p>"


# 获取链
@app.route('/chain/<string:node>', methods=['GET'])
def full_chain(node):
    response = {
        "chain": show_all(node),
        'length': length_block(node)
    }
    return flask.jsonify(response), 201


# 视图函数,浏览器输入localhost:5000/transactions/new
@app.route('/transactions/new/<string:node>', methods=['POST'])
def new_transactions(node):
    values = flask.request.get_json()
    required = ['sender', 'recipient', 'amount']
    # 遍历后有部分不在
    if not all(k in values for k in required):
        return "缺少参数", 400
    nodes[node].new_transaction(values['sender'], values['recipient'], values['amount'])
    response = {'message': f'交易会被添加到节点{node}'}
    return flask.jsonify(response), 201


# 这个函数里头有很多的问题
@app.route('/mine/<string:node>', methods=['GET'])
def mine(node):
    # 生成一个新块
    nodes[node].new_block()
    response = {"message":f"区块已经成功添加到{node}中"}
    return flask.jsonify(response), 200


# 共识算法
@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    blockchain.resolve_conflict()
    response = {'message': "当前链不符合规则,已被替换"}
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
