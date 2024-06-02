import string
import networkx as nx
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
import random
import queue


def openfile():
    """用户选择文件，返回文件路径"""
    window = tk.Tk()
    window.withdraw()
    return filedialog.askopenfilename()


def savefile():
    """用户选择保存文件，返回文件路径"""
    window = tk.Tk()
    window.withdraw()
    return filedialog.asksaveasfilename()


class Edge:
    def __init__(self, start, end, weight: int):
        self.start = start
        self.end = end
        self.weight = weight


class Graph:
    """存储有向图的数据结构"""

    def __init__(self):
        self.edge_list = []  # 存储边的临接表
        self.vertex_dict = {}  # 顶点字符串-标号查找表

    def addEdge(self, start: str, end: str):
        """添加边，权重为1，如果边存在则权重+1"""
        v1 = self.vertex_dict.get(start, None)
        v2 = self.vertex_dict.get(end, None)
        # 创建顶点
        if v1 is None:
            v1 = len(self.vertex_dict)
            self.vertex_dict[start] = v1
            self.edge_list.append([])
        if v2 is None:
            v2 = len(self.vertex_dict)
            self.vertex_dict[end] = v2
            self.edge_list.append([])
        # 边存在
        for edge in self.edge_list[v1]:
            if edge.end == end:
                edge.weight += 1
                return
        # 边不存在
        self.edge_list[v1].append(Edge(start, end, 1))

    def getEdgeList(self, vertex: str):
        """
        获取从某个顶点出发的边列表，也可以用于判断顶点是否存在
        返回值为None则顶点不存在，否则返回Edge组成的列表
        """
        v = self.vertex_dict.get(vertex, None)
        if v is None:
            return None
        return self.edge_list[v]


class WordGraph:
    def __init__(self):
        self.graph = Graph()

    def generateGraph(self, filepath):
        """用户选择文件，根据文件生成图，保存在self.graph"""
        # 将句子去除标点并划分为token
        tokens = list()
        lines = open(filepath, encoding='utf-8').readlines()
        for i in range(len(lines)):
            for piece in lines[i]:
                if piece in string.punctuation:
                    # 遍历每个句子的每个字母，如果发现是标点（在string.punctuation）中就替换为空格
                    lines[i] = lines[i].replace(piece, " ")
            tokens = tokens + lines[i].split()

        # token转小写
        for i in range(len(tokens)):
            tokens[i] = tokens[i].lower()

        # 将token加入图
        for i in range(len(tokens) - 1):
            self.graph.addEdge(start=tokens[i], end=tokens[i + 1])

    def showDirectedGraph(self):
        """画self.graph"""
        g = nx.DiGraph()  # 有向图
        g.add_nodes_from(node for node in self.graph.vertex_dict.keys())
        for i in self.graph.vertex_dict.values():
            i_start_edges = self.graph.edge_list[int(i)]
            for node_end, j in self.graph.vertex_dict.items():
                for edge in i_start_edges:
                    if edge.end == node_end:
                        g.add_edge(edge.start, edge.end, weight=edge.weight)

        pos = nx.spring_layout(g, iterations=20)
        weights = nx.get_edge_attributes(g, "weight")
        nx.draw_networkx(g, pos)
        nx.draw_networkx_edge_labels(g, pos, edge_labels=weights)

        plt.savefig("img.png")
        plt.show()

    def queryBridgeWords(self, word1: str, word2: str):
        """查询word1到word2之间的桥接词"""
        # 转小写
        word1 = word1.lower()
        word2 = word2.lower()

        if self.graph.getEdgeList(word1) is None:
            return -1

        if self.graph.getEdgeList(word2) is None:
            return -2

        bridge_words = list()
        for edge_1 in self.graph.getEdgeList(word1):
            word3 = edge_1.end
            for edge_3 in self.graph.getEdgeList(word3):
                if word2 == edge_3.end:
                    bridge_words.append(edge_1.end)

        if len(bridge_words) == 0:
            return -3
        else:
            return bridge_words

    def generateNewText(self, line):
        """根据bridge word生成新文本"""
        # 将新句子拆分为token
        for piece in line:
            if piece in string.punctuation:
                # 为防止最后打印结果时标点丢失，遍历每个句子的每个字母，如果发现是标点就在前面加一个空格，使其在下一步时形成一个token
                line = line.replace(piece, f" {piece}")
        tokens = line.split()

        # token转小写
        for i in range(len(tokens)):
            tokens[i] = tokens[i].lower()

        # 查桥接词，查到就放到新文本tokens列表中的对应位置
        for i in range(len(tokens) - 1):
            bridge_words = self.queryBridgeWords(tokens[i], tokens[i + 1])
            if bridge_words not in [-1, -2, -3]:
                for j in range(len(bridge_words)):
                    tokens.insert(i + j + 1, bridge_words[j])

        # 将tokens列表合并为一个句子
        sentence = str()
        for token in tokens:
            sentence = sentence + token + " "

        return sentence

    def calcShortestPath(self, word1: str, word2: str):
        # 堆优化Dijkstra
        word1 = word1.lower()
        dis = [1e9] * len(self.graph.vertex_dict)
        dis[self.graph.vertex_dict[word1]] = 0
        vis = [False] * len(self.graph.vertex_dict)
        q = queue.PriorityQueue()
        q.put((0, word1))
        while not q.empty():
            d, u = q.get()
            if vis[self.graph.vertex_dict[u]]:
                continue
            vis[self.graph.vertex_dict[u]] = True
            for edge in self.graph.getEdgeList(u):
                if dis[self.graph.vertex_dict[edge.end]] > dis[self.graph.vertex_dict[u]] + edge.weight:
                    dis[self.graph.vertex_dict[edge.end]] = dis[self.graph.vertex_dict[u]] + edge.weight
                    q.put((dis[self.graph.vertex_dict[edge.end]], edge.end))
        if word2 is None:
            return dis
        else:
            word2 = word2.lower()
            return dis[self.graph.vertex_dict[word2]]

    def randomWalk(self):
        start = random.choice(list(self.graph.vertex_dict.keys()))
        ret = start
        edge_tmp = []
        while True:  # 按Ctrl+C可终止（
            edge_list = self.graph.getEdgeList(start)
            # 无出边
            if edge_list is None or len(edge_list) == 0:
                break
            edge = random.choice(edge_list)
            ret = ret + " " + edge.end
            start = edge.end
            # 重复边
            if edge in edge_tmp:
                break
            edge_tmp.append(edge)
        return ret


def main():
    f = WordGraph()

    # generateGraph
    f.generateGraph(openfile())

    while True:
        a = input('1: showDirectedGraph\n'
                  '2: queryBridgeWords\n'
                  '3: generateNewText\n'
                  '4: calcShortestPath\n'
                  '5: randomWalk\n')
        if a == '1':
            # showDirectedGraph
            f.showDirectedGraph()
        elif  a == '2':
            # queryBridgeWords
            word_1 = input('input word1:')
            word_2 = input('input word2:')
            bridge_words = f.queryBridgeWords(word_1, word_2)
            if bridge_words == -1:
                print("No word1 in graph")
            elif bridge_words == -2:
                print("No word2 in graph")
            elif bridge_words == -3:
                print("No bridge words from word1 to word2")
            else:
                print(f"The bridge words from word1 to word2 are {bridge_words}")
        elif a == '3':
            # generateNewText
            line = input("Input text:")
            new_sentence = f.generateNewText(line)
            print(new_sentence)
        elif  a == '4':
            # calcShortestPath
            line = input('calcShortestPath: input 1 or 2 word(s):')
            words = line.split()
            if len(words) == 1:
                r = f.calcShortestPath(words[0], None)
                print('Distance from', words[0], 'to other words:')
                for i in range(len(r)):
                    print(list(f.graph.vertex_dict.keys())[
                          i], '\t:', r[i] == 1e9 and 'No path' or r[i])
            elif len(words) == 2:
                r = f.calcShortestPath(words[0], words[1])
                print('Distance from', words[0], 'to',
                      words[1], ': ', r == 1e9 and 'No path' or r)
            else:
                print('Invalid input')
        elif a == '5':
            # randomWalk
            rw = f.randomWalk()
            print('Random walk:', rw)
            f = savefile()
            if f != '':
                with open(f, 'w') as file:
                    file.write(rw)
        else:
            break


if __name__ == '__main__':
    main()

# S2R5
# R2后的修改
# R4后的修改
s2r7 = 'B2'
# S2R4
# IDE Plugin