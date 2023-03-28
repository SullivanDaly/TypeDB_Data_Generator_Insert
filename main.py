import random
import os
import time

from typedb.client import *

DBNAME = "purchase_test"
NB_LINE = 8000
NB_FILE = 100
NB_ITEM = 160000000


# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

def loadDataset():
    with TypeDB.core_client("localhost:1729") as client:
        if client.databases().contains(DBNAME):
            print("The purchase database exists already.")
            answerUser = input("Do you want to delete it? Yes or No: ")
            if answerUser.lower() == "yes":
                client.databases().get(DBNAME).delete()
                print("DataBase Deleted")
                client.databases().create(DBNAME)
                print("Database Created")
        else:
            client.databases().create(DBNAME)
            print("Database Created")

        with client.session(DBNAME, SessionType.SCHEMA) as session:
            with open(os.path.join("purchase_schema.tql"), "r") as file:
                schema = file.read()
                with session.transaction(TransactionType.WRITE) as transaction:
                    try:
                        transaction.query().define(schema)
                        transaction.commit()
                        print("Schema loaded")
                    except Exception as e:
                        print(e)
                        print("Schema Failed to load")

        with client.session(DBNAME, SessionType.DATA) as session:
            start = time.time()
            for nbFile in range(0, NB_FILE):
                with open(os.path.join("purchase_data" + str(nbFile) + ".tql"), "r") as file:
                    print("READ FILE " + str(nbFile))
                    i = 1  # not zero to not trigger i % NBLINE
                    commit_cmpt = 1
                    query = ""
                    data = file.readlines()
                    nbLines = len(data)
                    print(str(nbLines) + " lines")
                    transaction = session.transaction(TransactionType.WRITE)
                    for line in data:
                        if not (i % NB_LINE - 1):  # to trigger on i = 1
                            transaction = session.transaction(TransactionType.WRITE)

                        query += line
                        if not (i % 8):
                            transaction.query().insert(query)
                            if not (i % NB_LINE):
                                transaction.commit()
                                print("FILE " + str(nbFile) + ": commit " + str(commit_cmpt) + " on " +
                                      str(nbLines // NB_LINE))
                                commit_cmpt += 1
                            query = ""
                        i += 1
                    print("FILE " + str(nbFile) + " LOADED")
            stop = time.time()
            print("DATA LOADED in -> " + str(stop - start) + "s")


def datasetGenerator():
    # Use a breakpoint in the code line below to debug your script.
    currencyTab = ["EUR", "GBP", "USD"]
    maxPrice = 1000
    i = 0

    start = time.time()

    for b in range(NB_FILE):

        with open('purchase_data' + str(b) + '.tql', 'a') as dataFile:

            for j in range(NB_ITEM // NB_FILE):
                currentLine1 = "insert $i isa item, has item_id " + str(i)
                currentLine1 += ", has description " + '"' + str(i) + '"' + ";\n"
                price = random.randint(1, maxPrice)
                currencyIndice = random.randint(0, 2)
                currentLine2 = "$p isa price; $p " + str(price) + ";\n"
                currentLine3 = "$c isa currency; $c " + '"' + currencyTab[currencyIndice] + '";\n'
                currentLine4 = "$r1(price: $p, currency: $c, item: $i) isa item_pricing_sub;\n"
                currentLine5 = "$r2(price: $p, currency: $c, item: $i) isa item_pricing_direct;\n"
                currentLine6 = "$r3(item: $i) isa item_pricing_own, has price $p, has currency $c;\n"
                currentLine7 = "$pe isa price_entity, has price $p, has currency $c;\n"
                currentLine8 = "$r4(item: $i, price_entity: $pe) isa item_pricing_entity;\n"
                i += 1

                dataFile.write(currentLine1)
                dataFile.write(currentLine2)
                dataFile.write(currentLine3)
                dataFile.write(currentLine4)
                dataFile.write(currentLine5)
                dataFile.write(currentLine6)
                dataFile.write(currentLine7)
                dataFile.write(currentLine8)
            print("Done with file " + str(j + 1) + " on " + str(NB_FILE))
    stop = time.time()
    print("DATA GENERATED in -> " + str(stop - start) + "s")


if __name__ == '__main__':
    answer = 0
    while not (answer in range(1, 4)):
        print("Do you want to :")
        print("1) Generate Data")
        print("2) Load Data")
        print("3) Quit")
        answer = int(input("1 or 2 or 3? "))
    if answer == 1:
        datasetGenerator()
    if answer == 2:
        loadDataset()
