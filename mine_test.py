from itertools import batched
import numpy as np
my_list = [i for i in range(1, 25)]
chunk_size = 5
chunk_keeper = []
# batched returns an iterator; convert to a list to see all chunks
for i in range(1, 25):

    #chunks = list(batched(my_list, chunk_size))
    chunk_keeper.append(my_list)


#new_cs = 5
#new_chunks = list(batched(chunk_keeper, new_cs))
item_counter = 1
for item in chunk_keeper:
    print(item_counter)
    print('item: ',item)
    item_counter += 1


    for i in range(len(chunk_keeper)):
        fe = [sublist[i] for sublist in chunk_keeper]
        print("fe: ",fe)
        print("fe len: ", len(fe))
"""print("shape: ",np.shape(new_chunks))
for i in range(len(new_chunks)):

    for e in range(len(new_chunks[i])):
        print(f"{i}: ", new_chunks[i][e])
        hh = 0
        for n in range(len(new_chunks[i][e])):
            print(f"{e}: ", new_chunks[i][e][n][hh])
        hh += 1
        for y in range(len(new_chunks[i][e][n])):
                print(f"{y}: ", new_chunks[i][e][n][y])
"""