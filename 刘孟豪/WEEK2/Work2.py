# 实现一个基于交叉熵（交叉熵）的多分类任务，任务可以自拟。  输出最小标量

# coding:utf8

import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt

class MultiTaskModel(nn.Module):
    def __init__(self, input_size, output_size):
        super(MultiTaskModel, self).__init__()
        # 线性层，input_size输入向量的维度
        self.linear = nn.Linear(input_size, output_size)
        self.activation = torch.sigmoid  # sigmoid归一化函数
        self.loss = nn.functional.cross_entropy  # loss函数采用交叉熵

    # 当输入真实标签，返回loss值；无真实标签，返回预测值
    def forward(self, x, y=None):
        x = self.linear(x) # (batch_size, input_size) -> (batch_size, 1)
        y_pred = self.activation(x)  # (batch_size, 1) -> (batch_size, 1)
        if y is not None:
            return self.loss(y_pred, y)  # 预测值和真实值计算损失
        else:
            return y_pred  # 输出预测结果


# 生成一个样本, 样本的生成方法，代表了我们要学习的规律
def build_sample():
    x = np.random.random(5)
    # 获取最小值的索引
    # abs_v = np.abs(x)
    # argmin_idx = np.argmin(x)
    argmin_idx = np.argmax(x)
    return x, argmin_idx


# 随机生成一批样本
# 正负样本均匀生成
def build_dataset(total_sample_num):
    X = []
    Y = []
    for i in range(total_sample_num):
        x, y = build_sample()
        X.append(x)
        Y.append(y)
    return torch.FloatTensor(X), torch.LongTensor(Y)

# 测试代码
# 用来测试每轮模型的准确率
def evaluate(model):
    model.eval()
    test_sample_num = 100
    # 获取训练样本
    x, y = build_dataset(test_sample_num)
    correct, wrong = 0, 0
    # 不进行梯度计算。这个上下文管理器的主要作用是提高代码的执行效率，尤其是在推断阶段
    with torch.no_grad():
        y_pred = model(x)  # 模型预测，获取与预测值
        for y_p, y_t in zip(y_pred, y):  # 与真实标签进行对比
            #如果对应值是最小值
            # abs_v = np.abs(y_p)
            # if np.argmin(y_p) == int(y_t):
            if np.argmax(y_p) == int(y_t):
                correct += 1
            else:
                wrong += 1
    print("正确预测个数：%d, 正确率：%f" % (correct, correct / (correct + wrong)))
    return correct / (correct + wrong)


def main():
    # 配置参数
    epoch_num = 20  # 训练轮数
    batch_size = 20  # 每次训练样本个数
    train_sample = 5000  # 每轮训练总共训练的样本总数
    input_size = 5  # 输入向量维度
    learning_rate = 0.001  # 学习率
    output_size = 5 #输出数据维度
    # 建立模型
    model = MultiTaskModel(input_size, output_size)
    # 选择优化器Adam
    optim = torch.optim.Adam(model.parameters(), lr=learning_rate)
    log = []
    # 获取自定义的训练集，正常任务是读取训练集
    train_x, train_y = build_dataset(train_sample)
    # 训练过程
    for epoch in range(epoch_num):
        model.train()
        watch_loss = []
        # // 整除
        for batch_index in range(train_sample // batch_size):
            # 列表索引，分片
            x = train_x[batch_index * batch_size: (batch_index + 1) * batch_size]
            y = train_y[batch_index * batch_size: (batch_index + 1) * batch_size]
            loss = model(x, y)  # 模型计算loss，会执行forword()
            loss.backward()  # 损失函数计算梯度
            optim.step()  # 优化器更新权重
            optim.zero_grad()  # 梯度归零
            watch_loss.append(loss.item())
        # print("=========\n第%d轮平均loss:%f" % (epoch + 1, np.mean(watch_loss)))
        acc = evaluate(model)  # 测试本轮模型结果
        log.append([acc, float(np.mean(watch_loss))])
    # 保存模型
    torch.save(model.state_dict(), "model.pt")
    # 画图
    print(log)
    plt.plot(range(len(log)), [l[0] for l in log], label="acc")  # 画acc曲线
    plt.plot(range(len(log)), [l[1] for l in log], label="loss")  # 画loss曲线
    plt.legend()
    plt.show()
    return

# 使用训练好的模型做预测
def predict(model_path, input_vec):
    input_size = 5
    model = MultiTaskModel(input_size)
    model.load_state_dict(torch.load(model_path))  # 加载训练好的权重
    print(model.state_dict())

    model.eval()  # 测试模式
    with torch.no_grad():  # 不计算梯度
        result = model.forward(torch.FloatTensor(input_vec))  # 模型预测
    for vec, res in zip(input_vec, result):
        print("输入：%s, 预测类别：%d, 概率值：%f" % (vec, round(float(res)), res))  # 打印结果

if __name__ == "__main__":
    main()
    # test_vec = [[0.07889086, 0.15229675, 0.31082123, 0.03504317, 0.18920843],
    #             [0.94963533, 0.5524256, 0.95758807, 0.95520434, 0.84890681],
    #             [0.78797868, 0.67482528, 0.13625847, 0.34675372, 0.19871392],
    #             [0.79349776, 0.59416669, 0.92579291, 0.41567412, 0.1358894]]
    # predict("model.pt", test_vec)
