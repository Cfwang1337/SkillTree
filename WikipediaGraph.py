#!/usr/bin/python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from collections import defaultdict
import csv
import matplotlib.pyplot as plt
import networkx as net
import requests


def trim_nodes(g, degree=1):
    with open("subject_and_connection.csv", "wb") as writefile:
        fieldnames = ["subject", "connections"]
        writer = csv.DictWriter(writefile, fieldnames=fieldnames)
        writer.writeheader()

        g2 = g.copy()
        d = net.degree(g2)
        for n in g.nodes():
            writer.writerow(dict(
                subject=n,
                connections=d[n]
            ))
            # print n, d[n]
            if d[n] <= degree:
                g2.remove_node(n)
        return g2


def trim_edges(g, weight):
    g2 = net.DiGraph()
    for f, to, edata in g.edges(data=True):
        # print f, to, edata
        if edata['followers'] >= weight:
            g2.add_edge(f, to, followers=edata['followers'])
    return g2


def analyze_follows():

    o = net.DiGraph()

    with open("follower_list.csv", "rb") as readfile:
        reader = csv.DictReader(readfile)
        for row in reader:
            o.add_edge(row['Source'], row['Target'], followers=row['followers'])

    print 'Graph size: ', len(o)
    o = trim_nodes(o, degree=1)
    print "After node pruning: ", len(o)
    o = trim_edges(o, weight=1)
    print "After edge pruning: ", len(o)

    pos = net.spring_layout(o)

    plt.axis('off')

    ns_list = []

    for node in o.nodes:
        if len(list(o[node])) > 0:
            nodesize = int(o[node][list(o[node])[0]]['followers'])
        else:
            nodesize = 1
        ns_list.append(nodesize)

        x, y = pos[node]

        plt.text(x, y, s=node, alpha=1.0, horizontalalignment='center', fontsize=5)

    net.draw_networkx_nodes(o, pos, node_color='g', node_size=ns_list, alpha=0.5)
    net.draw_networkx_edges(o, pos, width=0.1, alpha=0.15)

    plt.show()


    #TODO NEED TO IDENTIFY DIFFERENT CLUSTERS
    #TODO NEED DIFFERENT COLORS FOR DIFFERENT CLUSTERS

    return


#TODO NEED TO USE IMAP
def followed_by_getter():
    prefix = "https://en.wikipedia.org/w/index.php?title=Special%3AWhatLinksHere&limit=500&target="
    suffix = "&namespace=0"

    with open("master_discipline_list.csv", 'rb') as readfile, open("follower_list.csv", "wb") as writefile:

        fieldnames = [
            "Source",
            "Target",
            "followers"
        ]
        writer = csv.DictWriter(writefile, fieldnames=fieldnames)
        writer.writeheader()

        reader = list(csv.DictReader(readfile))
        subjects = [row['element'] for row in reader]
        print "ALL SUBJECTS:", len(subjects)
        for subject in subjects:
            print subject
            next_page = True

            address = "{0}{1}{2}".format(prefix, subject, suffix)
            followers_subsetted = []

            while next_page is True:
                # print address
                page = requests.get(address, timeout=30)
                souper = BeautifulSoup(page.content, "html.parser")

                if souper.find('ul', {'id': 'mw-whatlinkshere-list'}) is not None:
                    followers = souper.find('ul', {'id': 'mw-whatlinkshere-list'}).find_all('li')
                else:
                    break

                for follower in followers:
                    follower_prospect = follower.a.attrs.get('href').replace('/wiki/', '').lower()
                    if follower_prospect in subjects:
                        followers_subsetted.append(follower_prospect)

                #TODO THIS IS WRONG
                next_index = souper.find('hr').find_next('a')
                next_next_index = next_index.find_next('a')

                if "next 500" in next_index.getText():
                    next_page = True
                    address = "http://en.wikipedia.org{0}".format(next_index.attrs.get('href'))
                elif "next 500" in next_next_index.getText():
                    next_page = True
                    address = "http://en.wikipedia.org{0}".format(next_next_index.attrs.get('href'))
                else:
                    next_page = False

            # print "FOLLOWER SUBSET:", len(followers_subsetted)

            for sub_follower in followers_subsetted:
                writer.writerow(dict(
                    subject=subject,
                    followed_by=sub_follower,
                    followers=len(followers_subsetted)
                ))


def wikipedia_getter():

    with open("master_discipline_list.csv", 'wb') as writefile:
        fieldnames = [
            "element"
        ]

        writer = csv.DictWriter(writefile, fieldnames=fieldnames)
        writer.writeheader()

        master_address = "http://en.wikipedia.org/wiki/List_of_academic_disciplines_and_sub-disciplines"

        page = requests.get(master_address, timeout=30)
        souper = BeautifulSoup(page.content, "html.parser")

        column_blocks = souper.find_all("div", {"class": "div-col columns column-count column-count-2"})

        children = []
        for iteration in column_blocks:

            parent_1_link = [item.attrs.get('href').replace("/wiki/", "").lower() for item in iteration.find_previous('h2').find_next('div').find_all('a')\
                             if "Outline_" not in item.attrs.get('href')]

            parent_2_link = [item.attrs.get('href').replace("/wiki/", "").lower() for item in iteration.find_previous('h3').find_next('div').find_all('a')\
                             if "Outline_" not in item.attrs.get('href') and "List" not in item.attrs.get('href')]

            if len(parent_2_link) == 0:
                parent_2_link = [item.attrs.get('href').replace("/wiki/", "").lower() for item in iteration.find_previous('div').find_all('a') \
                 if "Outline_" not in item.attrs.get('href') and "List" not in item.attrs.get('href')]

            for link in iteration.find_all('a'):
                if "Outline_" not in link.attrs.get('href') and "#" not in link.attrs.get('href'):
                    children.append(link.attrs.get('href').replace("/wiki/", "").lower())
            children.extend(parent_1_link)
            children.extend(parent_2_link)

        children = list(set(children))

        for child in children:
            print "\t\t", child

            writer.writerow({"element": child})

    return


def main():

    print "PLEASE CHOOSE"
    print "0. SCRAPE WIKIPEDIA ACADEMICS "
    print "1. ANALYZE FOLLOWS GRAPH "

    choice = raw_input("ENTER CHOICE: ")

    if choice == "0":
        wikipedia_getter()
        followed_by_getter()
    elif choice == "1":
        analyze_follows()
    return

if __name__ == "__main__":
    main()