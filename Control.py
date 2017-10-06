#!/usr/bin/python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import csv
import requests


#TODO MIGHT NEED TO USE IMAP
def followed_by_getter():
    prefix = "https://en.wikipedia.org/w/index.php?title=Special%3AWhatLinksHere&limit=500&target="
    suffix = "&namespace=0"

    with open("master_discipline_list.csv", 'rb') as readfile, open("follower_list.csv", "wb") as writefile:

        fieldnames = [
            "subject",
            "follower"
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
                print address
                page = requests.get(address, timeout=30)
                souper = BeautifulSoup(page.content, "html.parser")

                if souper.find('ul', {'id': 'mw-whatlinkshere-list'}) is not None:
                    followers = souper.find('ul', {'id': 'mw-whatlinkshere-list'}).find_all('li')
                else:
                    break

                for follower in followers:
                    follower_prospect = follower.a.attrs.get('href').replace('/wiki/','').lower()
                    if follower_prospect in subjects:
                        followers_subsetted.append(follower_prospect)

                next_index = souper.find('hr').find_next('a')

                if "next 500" in next_index.getText():
                    next_page = True
                    address = "http://en.wikipedia.org{0}".format(next_index.attrs.get('href'))
                else:
                    next_page = False

            print "FOLLOWER SUBSET:", len(followers_subsetted)

            for sub_follower in followers_subsetted:
                writer.writerow(dict(
                    subject=subject,
                    follower=sub_follower
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
                if "Outline_" not in link.attrs.get('href'):
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
    print "0. SCRAPE WIKIPEDIA ACADEMICS MAIN PAGE "
    print "1. SCRAPE WIKIPEDIA FOLLOWS "
    # print "1. SCRAPE COURSE CATALOGS "

    choice = raw_input("ENTER CHOICE: ")

    if choice == "0":
        wikipedia_getter()
    elif choice == "1":
        followed_by_getter()
    return

if __name__ == "__main__":
    main()