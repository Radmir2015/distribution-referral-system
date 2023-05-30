from dataclasses import dataclass, field
import math
from typing import List, Union
from uuid import uuid4
import netgraph

@dataclass
class Referrer:
    name: str
    referral_percentage: float
    id: str = field(default_factory=lambda: str(uuid4()))

@dataclass
class Product:
    name: str
    price: float
    id: str = field(default_factory=lambda: str(uuid4()))

@dataclass
class ReferralLink:
    referrer: Referrer
    product: Product
    level: int = 0
    children: List[Union['ReferralLink', List['ReferralLink']]] = field(default_factory=list)

    def add_child(self, child: 'ReferralLink'):
        self.children.append(child)

    def calculate_commission(self, amount: float = None) -> float:
        if amount is None:
            amount = self.product.price

        commission = amount * self.referrer.referral_percentage
        # print(f'Commision: {commission}, amount: {amount}, name: {self.referrer.name}, perc: {self.referrer.referral_percentage}')

        for child in self.children:
            if isinstance(child, ReferralLink):
                commission += child.calculate_commission(amount)
            elif isinstance(child, list):
                for nested_child in child:
                    commission += nested_child.calculate_commission(amount * self.referrer.referral_percentage)

        return commission

# Example usage
# referrer1 = Referrer(name="Company 1", referral_percentage=0.1)
# referrer2 = Referrer(name="Company 2", referral_percentage=0.05)
# referrer3 = Referrer(name="Individual 1", referral_percentage=0.02)

# product = Product(name="Bank Product", price=1000)

# referral_link1 = ReferralLink(referrer=referrer1, product=product)
# referral_link2 = ReferralLink(referrer=referrer2, product=product, level=1)
# referral_link3 = ReferralLink(referrer=referrer3, product=product, level=1)

# referral_link1.add_child(referral_link2)
# referral_link1.add_child([referral_link3])

# commission = referral_link1.calculate_commission()
# print(f"Total commission: ${commission:.2f}")

def print_referral_structure(referral_link: 'ReferralLink', indent: int = 0):
    print(" " * indent + f"Referrer: {referral_link.referrer.name}, ({referral_link.product.name}, award: {referral_link.calculate_commission()}$)")
    for child in referral_link.children:
        if isinstance(child, ReferralLink):
            print_referral_structure(child, indent + 4)
        elif isinstance(child, list):
            for nested_child in child:
                print_referral_structure(nested_child, indent + 4)

# Example usage
# print_referral_structure(referral_link1)

import networkx as nx
import matplotlib.pyplot as plt

# def build_graph(referral_link: 'ReferralLink', graph=None, parent_name=None):
#     if graph is None:
#         graph = nx.DiGraph()

#     referrer_name = referral_link.referrer.name
#     graph.add_node(referrer_name)

#     if parent_name is not None:
#         graph.add_edge(parent_name, referrer_name)

#     for child in referral_link.children:
#         if isinstance(child, ReferralLink):
#             build_graph(child, graph, referrer_name)
#         elif isinstance(child, list):
#             for nested_child in child:
#                 build_graph(nested_child, graph, referrer_name)

#     return graph

def build_graph(referral_link: 'ReferralLink', graph=None, parent_name=None, parent_commission=0.0):
    if graph is None:
        graph = nx.DiGraph()

    referrer_name = referral_link.referrer.name
    commission = referral_link.calculate_commission()
    graph.add_node(referrer_name, commission=commission)

    if parent_name is not None:
        graph.add_edge(parent_name, referrer_name, weight=commission)
        # graph.add_edge(parent_name, referrer_name, weight=f'{commission} - {parent_commission}')

    for child in referral_link.children:
        if isinstance(child, ReferralLink):
            build_graph(child, graph, referrer_name, commission)
        elif isinstance(child, list):
            for nested_child in child:
                build_graph(nested_child, graph, referrer_name, commission)

    return graph

# def draw_graph(graph):
#     pos = nx.spring_layout(graph)
#     nx.draw_networkx_nodes(graph, pos, cmap=plt.get_cmap('jet'), node_size = 500)
#     nx.draw_networkx_labels(graph, pos)
#     nx.draw_networkx_edges(graph, pos, edgelist=graph.edges(), edge_color='r', arrows=True)
#     plt.show()

def draw_graph(graph):
    # pos = nx.spring_layout(graph, k=0.65, iterations=20)  # change these parameters to change spacing
    pos = nx.circular_layout(graph)  # change these parameters to change spacing
    labels = nx.get_edge_attributes(graph, 'weight')
    node_sizes = [math.sqrt(graph.nodes[n]["commission"]) * 100 for n in graph.nodes()]
    nx.draw_networkx_nodes(graph, pos, node_size=node_sizes, cmap=plt.get_cmap('jet'))
    nx.draw_networkx_labels(graph, pos)
    nx.draw_networkx_edges(graph, pos, edgelist=graph.edges(), edge_color='r', arrows=True, arrowstyle='-|>', arrowsize=40)
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels, label_pos=0.3, bbox=dict(alpha=0))
    plt.show()

# Example usage
# graph = build_graph(referral_link1)
# draw_graph(graph)

# # Инициализация рефереров
# referrer1 = Referrer(name="Company 1", referral_percentage=0.1)
# referrer2 = Referrer(name="Company 2", referral_percentage=0.05)
# referrer3 = Referrer(name="Individual 1", referral_percentage=0.02)
# referrer4 = Referrer(name="Company 3", referral_percentage=0.07)
# referrer5 = Referrer(name="Individual 2", referral_percentage=0.03)

# # Инициализация продуктов
# product1 = Product(name="Bank Product 1", price=1000)
# product2 = Product(name="Bank Product 2", price=2000)

# # Инициализация реферальных ссылок
# referral_link1 = ReferralLink(referrer=referrer1, product=product1)
# referral_link2 = ReferralLink(referrer=referrer2, product=product1, level=1)
# referral_link3 = ReferralLink(referrer=referrer3, product=product1, level=1)
# referral_link4 = ReferralLink(referrer=referrer4, product=product1, level=2)
# referral_link5 = ReferralLink(referrer=referrer5, product=product1, level=2)

# # Создание структуры дерева
# referral_link1.add_child([referral_link2])
# referral_link2.add_child([referral_link4])
# referral_link1.add_child([referral_link3])
# referral_link3.add_child([referral_link5])

# Инициализация рефереров
referrer1 = Referrer(name="Company 1", referral_percentage=0.1)
referrer2 = Referrer(name="Company 2", referral_percentage=0.05)
referrer3 = Referrer(name="Individual 1", referral_percentage=0.02)
referrer4 = Referrer(name="Company 3", referral_percentage=0.07)
referrer5 = Referrer(name="Individual 2", referral_percentage=0.03)
referrer6 = Referrer(name="Company 4", referral_percentage=0.06)
referrer7 = Referrer(name="Individual 3", referral_percentage=0.04)
referrer8 = Referrer(name="Company 5", referral_percentage=0.08)
referrer9 = Referrer(name="Individual 4", referral_percentage=0.01)
referrer10 = Referrer(name="Company 6", referral_percentage=0.09)
referrer11 = Referrer(name="Individual 5", referral_percentage=0.02)
referrer12 = Referrer(name="Company 7", referral_percentage=0.05)

# Инициализация продуктов
product1 = Product(name="Bank Product 1", price=1000)
product2 = Product(name="Bank Product 2", price=2000)
product3 = Product(name="Bank Product 3", price=1500)
product4 = Product(name="Bank Product 4", price=2500)

# Инициализация реферальных ссылок
referral_link1 = ReferralLink(referrer=referrer1, product=product1)
referral_link2 = ReferralLink(referrer=referrer2, product=product1, level=1)
referral_link3 = ReferralLink(referrer=referrer3, product=product2, level=2)
referral_link4 = ReferralLink(referrer=referrer4, product=product2, level=3)
referral_link5 = ReferralLink(referrer=referrer5, product=product3, level=1)
referral_link6 = ReferralLink(referrer=referrer6, product=product3, level=2)
referral_link7 = ReferralLink(referrer=referrer7, product=product4, level=1)
referral_link8 = ReferralLink(referrer=referrer8, product=product4, level=2)
referral_link9 = ReferralLink(referrer=referrer9, product=product1, level=3)
referral_link10 = ReferralLink(referrer=referrer10, product=product2, level=1)
referral_link11 = ReferralLink(referrer=referrer11, product=product3, level=3)
referral_link12 = ReferralLink(referrer=referrer12, product=product4, level=1)

# Создание структуры дерева
referral_link1.add_child(referral_link2)
referral_link2.add_child(referral_link3)
referral_link3.add_child(referral_link4)
referral_link5.add_child(referral_link6)
referral_link7.add_child(referral_link8)
referral_link9.add_child(referral_link10)
referral_link11.add_child(referral_link12)
referral_link1.add_child([referral_link5, referral_link7, referral_link9, referral_link11])

print_referral_structure(referral_link1)

commission = referral_link1.calculate_commission()
print(f"Total commission: ${commission:.2f}")

# Визуализация графа
graph = build_graph(referral_link1)
draw_graph(graph)

# # Визуализация графа
graph = build_graph(referral_link1)

# Выберем расположение узлов с помощью spring_layout
pos = nx.spring_layout(graph)

import numpy as np
np.seterr(divide='ignore', invalid='ignore')

# Создайте интерактивный граф с помощью netgraph
# Не забудьте сохранить ссылку на объект plot_instance!
plot_instance = netgraph.InteractiveGraph(graph, node_positions=pos)
plt.show()