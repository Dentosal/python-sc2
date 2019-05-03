import numpy as np
import perfplot
from scipy.spatial.distance import cdist, pdist, squareform


def func_cdist(arr):
    return cdist(arr, arr)


def func_pdist(arr):
    return pdist(arr)


def func_transpose(arr):
    z = np.array([[complex(c[0], c[1]) for c in arr]])  # notice the [[ ... ]]
    return abs(z.T - z)


def func_newaxis(arr):
    return np.sqrt(np.sum((arr[:, np.newaxis, :] - arr[np.newaxis, :, :]) ** 2, axis=-1))


def func_newaxis2(arr):
    return (np.sum((arr[:, np.newaxis, :] - arr[np.newaxis, :, :]) ** 2, axis=-1)) ** 0.5


# perfplot.show(
#     setup=lambda n: np.random.rand(n, 2),
#     kernels=[func_cdist, func_pdist],
#     # kernels=[func_cdist, func_transpose, func_newaxis, func_newaxis2],
#     n_range=[k * 100 for k in range(1, 31)],
#     logx=True,
#     logy=True,
#     xlabel="len(array)",
# )
# def einsum_sqrt(a):
#     return np.sqrt(np.einsum('ij,ij->i', a, a))
# def compute_distances_no_loops(self, X):
#     dists = -2 * np.dot(X, self.X_train.T) + np.sum(self.X_train**2,    axis=1) + np.sum(X**2, axis=1)[:, np.newaxis]
#     return dists
n = 4
test = np.random.rand(n, 2)
print(test)
other = func_cdist(test)
print(other)
other = func_newaxis(test)
print(other)
other = func_newaxis2(test)
print(other)
other = func_transpose(test)
print(other)
other = func_pdist(test)
print(other)
# square = squareform(other)
# print(square)
# other = linalg(test)
# print(other)
# def look_up(a,b):
#     result(abs(a-b)+a*b)
#     print(a,b,result)
#     return abs(a-b)+a*b

# for a,b in ((x,y) for x in range(4) for y in range(4)):
    # look_up(a,b)


# print(0, 1, 0)
# print(0, 2, 1)
# print(0, 3, 2)
# print(1, 0, 0)
# print(1, 2, 4)
# print(1, 3, 5)
# print(2, 0, 1)
# print(2, 1, 4)
# print(2, 3, 6)
# print(3, 0, 2)
# print(3, 1, 5)
# print(3, 2, 6)

# x = np.random.random((3,3))
# print(x)'
