# numba/matrix.py
# this is gonna be an attempt to optimize matrix calculations with numba
# wish me luck

# TODO: dew it

from numba import njit, jit, cuda, float32, prange


class JITMatrix:
    @staticmethod
    @jit
    def add(a, b, c): # reference: c = a + b
        for i in prange(len(a)):
            for j in range(len(a[0])):
                c[i][j] += b[i][j]

    @staticmethod
    @cuda.jit
    def fast_matmul(A, B, C, TPB):
        # C = A * B
        # Define an array in the shared memory
        # The size and type of the arrays must be known at compile time
        sA = cuda.shared.array(shape=(TPB, TPB), dtype=float32)
        sB = cuda.shared.array(shape=(TPB, TPB), dtype=float32)

        x, y = cuda.grid(2)

        tx = cuda.threadIdx.x
        ty = cuda.threadIdx.y
        bpg = cuda.gridDim.x  # blocks per grid

        if x >= C.shape[0] and y >= C.shape[1]:
            # Quit if (x, y) is outside valid C boundary
            return

        # Each thread computes one element in the result matrix.
        # The dot product is chunked into dot products of TPB-long vectors.
        tmp = 0.
        for i in range(bpg):
            # Preload data into shared memory
            sA[tx, ty] = A[x, ty + i * TPB]
            sB[tx, ty] = B[tx + i * TPB, y]

            # Wait until all threads finish preloading
            cuda.syncthreads()

            # Computes partial product on the shared memory
            for j in range(TPB):
                tmp += sA[tx, j] * sB[j, ty]

            # Wait until all threads finish computing
            cuda.syncthreads()
