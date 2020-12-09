import numpy as np
import matplotlib.pyplot as plt
'''
Computes the L1 distance between two given images.
'''
def distance(a,b):
    dist = 0
    dims = a.shape
    for i in range(dims[0]):
        for j in range(dims[1]):
            dist += abs(a[i][j] - b[i][j])
    return dist

'''
Retrieves the closest image from a given one by using a brute force algorithm
'''
def brute_force_closest(im_id,data):
    id = 0
    min_dist = distance(data[im_id],data[0])
    for i in range(1,1500):
        im_dist = distance(data[im_id],data[i])
        if im_dist < min_dist:
            id = i
            min_dist = im_dist
    return id,min_dist


def main():
    data = np.load('./images.npy')
    x = int(input("Introduce index for comparison: "))+1499
    if x < data.shape[0]:
        id, min_dist = brute_force_closest(x,data)
        fig = plt.figure()
        fig.set_figwidth(10)
        fig.set_figheight(10)
        sp1 = fig.add_subplot(1,2,1)
        sp1.imshow(data[x], cmap=plt.cm.gray, interpolation="lanczos")
        sp1 = fig.add_subplot(1,2,2)
        sp1.imshow(data[id], cmap=plt.cm.gray, interpolation="lanczos")
        plt.show()
        print(min_dist)

if __name__ == "__main__":
    main()
