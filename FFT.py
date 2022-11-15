"""Implementation of fast fourier transform algorithm"""

import math
import cmath
import numpy as np

def fft(x):
    """Compute the discrete Fourier Transform of the 1D array x"""
    x = np.asarray(x, dtype=float)
    N = x.shape[0]

    if np.log2(N) % 1 > 0:
        raise ValueError("size of x must be a power of 2")

    # N_min here is equivalent to the stopping condition above,
    # and should be a power of 2
    N_min = min(N, 32)

    # Perform an O[N^2] DFT on all length-N_min sub-problems at once
    n = np.arange(N_min)
    k = n[:, None]
    M = np.exp(-2j * np.pi * n * k / N_min)
    x = np.dot(M, x.reshape((N_min, -1)))

    # build-up each level of the recursive calculation all at once
    while x.shape[0] < N:
        x_even = x[:, :x.shape[1] / 2]
        x_odd = x[:, x.shape[1] / 2:]
        factor = np.exp(-1j * np.pi * np.arange(x.shape[0])
                        / x.shape[0])[:, None]
        x = np.vstack([x_even + factor * x_odd,
                       x_even - factor * x_odd])

    return x.ravel()

def ifft(x):
    """Compute the inverse discrete Fourier Transform of the 1D array x"""
    return fft(x).conj() / len(x)

def fft2(x):
    """Compute the 2-dimensional discrete Fourier Transform"""
    return np.fft.fft2(x)

def ifft2(x):
    """Compute the 2-dimensional inverse discrete Fourier Transform"""
    return np.fft.ifft2(x)

def fftfreq(n, d=1.0):
    """Return the Discrete Fourier Transform sample frequencies"""
    if not isinstance(n, int) or n < 0:
        raise ValueError("n = %s is not valid.  n must be a nonnegative "
                         "integer." % n)
    val = 1.0 / (n * d)
    results = np.empty(n, int)
    N = (n - 1) // 2 + 1
    p1 = np.arange(0, N, dtype=int)
    results[:N] = p1
    p2 = np.arange(-(n // 2), 0, dtype=int)
    results[N:] = p2
    return results * val

def fftshift(x, axes=None):
    """Shift the zero-frequency component to the center of the spectrum."""
    x = np.asarray(x)
    if axes is None:
        axes = range(x.ndim)
    for k in axes:
        n = x.shape[k]
        p2 = (n + 1) // 2
        mylist = [slice(None)] * x.ndim
        mylist[k] = slice(p2, None)
        p1 = slice(0, p2)
        mylist[k] = p1
        x = np.concatenate((x[mylist], x), axis=k)
    return x

def ifftshift(x, axes=None):
    """The inverse of fftshift."""
    x = np.asarray(x)
    if axes is None:
        axes = range(x.ndim)
    for k in axes:
        n = x.shape[k]
        if n % 2 == 0:
            p1 = slice(n // 2, None)
            p2 = slice(0, n // 2)
        else:
            p1 = slice((n - 1) // 2, None)
            p2 = slice(0, (n - 1) // 2)
        mylist = [slice(None)] * x.ndim
        mylist[k] = p1
        x = np.concatenate((x, x[mylist]), axis=k)
        mylist[k] = p2
        x = x[mylist]
    return x

def rfft(x, n=None):
    """Compute the one-dimensional discrete Fourier Transform for real input"""
    x = np.asarray(x, dtype=float)
    if n is None:
        n = x.shape[0]

    if n < x.shape[0]:
        raise ValueError("n = %s is less than x.shape[0] = %s" % (n, x.shape[0]))
    elif n > x.shape[0]:
        x = np.resize(x, (n,))

    # Perform an O[N log N] complex-to-complex FFT
    X = fft(x)

    # build the weight vector
    w = np.empty(n // 2 + 1, complex)
    w.real = np.cos(np.pi * np.arange(n // 2 + 1) / n)
    w.imag = np.sin(np.pi * np.arange(n // 2 + 1) / n)

    return w * X[:n // 2 + 1]

def irfft(x, n=None):
    """Compute the inverse of rfft"""
    x = np.asarray(x, dtype=complex)
    if n is None:
        n = (x.shape[0] - 1) * 2

    # build the weight vector
    w = np.empty(n // 2 + 1, complex)
    w.real = np.cos(np.pi * np.arange(n // 2 + 1) / n)
    w.imag = np.sin(np.pi * np.arange(n // 2 + 1) / n)

    X = np.empty(n, complex)
    X[:n // 2 + 1] = x * w
    X[n // 2 + 1:] = x[-2:0:-1].conj() * w[1:-1]

    return ifft(X).real

def rfft2(x, s=None):
    """Compute the 2-dimensional discrete Fourier Transform for real input"""
    x = np.asarray(x, dtype=float)
    if s is None:
        s = x.shape

    if s[0] < x.shape[0] or s[1] < x.shape[1]:
        raise ValueError("s = %s is less than x.shape = %s" % (s, x.shape))
    elif s[0] > x.shape[0] or s[1] > x.shape[1]:
        x = np.resize(x, s)

    # Perform an O[N log N] complex-to-complex FFT
    X = fft2(x)

    # build the weight vectors
    w1 = np.empty(s[0] // 2 + 1, complex)
    w1.real = np.cos(np.pi * np.arange(s[0] // 2 + 1) / s[0])
    w1.imag = np.sin(np.pi * np.arange(s[0] // 2 + 1) / s[0])
    w2 = np.empty(s[1] // 2 + 1, complex)
    w2.real = np.cos(np.pi * np.arange(s[1] // 2 + 1) / s[1])
    w2.imag = np.sin(np.pi * np.arange(s[1] // 2 + 1) / s[1])

    return w1[:, None] * X[:s[0] // 2 + 1, :s[1] // 2 + 1] * w2

def irfft2(x, s=None):
    """Compute the inverse of rfft2"""
    x = np.asarray(x, dtype=complex)
    if s is None:
        s = (x.shape[0] - 1) * 2, (x.shape[1] - 1) * 2

    # build the weight vectors
    w1 = np.empty(s[0] // 2 + 1, complex)
    w1.real = np.cos(np.pi * np.arange(s[0] // 2 + 1) / s[0])
    w1.imag = np.sin(np.pi * np.arange(s[0] // 2 + 1) / s[0])
    w2 = np.empty(s[1] // 2 + 1, complex)
    w2.real = np.cos(np.pi * np.arange(s[1] // 2 + 1) / s[1])
    w2.imag = np.sin(np.pi * np.arange(s[1] // 2 + 1) / s[1])

    X = np.empty(s, complex)
    X[:s[0] // 2 + 1, :s[1] // 2 + 1] = x * w1[:, None] * w2
    X[s[0] // 2 + 1:, :s[1] // 2 + 1] = x[-2:0:-1, :].conj() * w1[1:-1, None] * w2
    X[:s[0] // 2 + 1, s[1] // 2 + 1:] = x[:, -2:0:-1].conj() * w1[:, None] * w2[1:-1]
    X[s[0] // 2 + 1:, s[1] // 2 + 1:] = x[-2:0:-1, -2:0:-1] * w1[1:-1, None] * w2[1:-1]

    return ifft2(X).real

def rfftn(x, s=None, axes=None):
    """Compute the N-dimensional discrete Fourier Transform for real input"""
    x = np.asarray(x, dtype=float)
    if s is None:
        s = x.shape
    if axes is None:
        axes = range(x.ndim)

    if np.any(np.asarray(s)[axes] < np.asarray(x.shape)[axes]):
        raise ValueError("s = %s is less than x.shape = %s" % (s, x.shape))
    elif np.any(np.asarray(s)[axes] > np.asarray(x.shape)[axes]):
        x = np.resize(x, s)

    # Perform an O[N log N] complex-to-complex FFT
    X = fftn(x, axes=axes)

    # build the weight vectors
    w = []
    for k in axes:
        w.append(np.empty(s[k] // 2 + 1, complex))
        w[-1].real = np.cos(np.pi * np.arange(s[k] // 2 + 1) / s[k])
        w[-1].imag = np.sin(np.pi * np.arange(s[k] // 2 + 1) / s[k])

    # multiply the appropriate slices of X by the weights
    for k in axes:
        sl = [slice(None)] * x.ndim
        sl[k] = slice(None, s[k] // 2 + 1)
        X[tuple(sl)] *= w[k]

    return X

def irfftn(x, s=None, axes=None):
    """Compute the inverse of rfftn"""
    x = np.asarray(x, dtype=complex)
    if s is None:
        s = [n * 2 - 2 for n in x.shape]
    if axes is None:
        axes = range(x.ndim)

    # build the weight vectors
    w = []
    for k in axes:
        w.append(np.empty(s[k] // 2 + 1, complex))
        w[-1].real = np.cos(np.pi * np.arange(s[k] // 2 + 1) / s[k])
        w[-1].imag = np.sin(np.pi * np.arange(s[k] // 2 + 1) / s[k])

    # multiply the appropriate slices of X by the weights
    X = np.empty(s, complex)
    for k in axes:
        sl = [slice(None)] * x.ndim
        sl[k] = slice(None, s[k] // 2 + 1)
        X[tuple(sl)] = x[tuple(sl)] * w[k]

    # build the slices for the negative frequencies
    slices = []
    for k in axes:
        sl = [slice(None)] * x.ndim
        sl[k] = slice(s[k] // 2 + 1, None)
        slices.append(tuple(sl))

    # copy the appropriate slices of X
    for k in range(len(axes)):
        sl = slices[k]
        X[sl] = x[slices[k - 1]].conj()

    return ifftn(X, axes=axes).real

def hfft2(x, s=None):
    """Compute the 2D discrete Fourier Transform for Hermitian-symmetric input"""
    x = np.asarray(x, dtype=float)
    if s is None:
        s = x.shape
    if s[0] < x.shape[0] or s[1] < x.shape[1]:
        raise ValueError("s = %s is less than x.shape = %s" % (s, x.shape))
    elif s[0] > x.shape[0] or s[1] > x.shape[1]:
        x = np.resize(x, s)

    # Perform an O[N log N] complex-to-complex FFT
    X = fft2(x)

    # build the weight vectors
    w1 = np.empty(s[0] // 2 + 1, complex)
    w1.real = np.cos(np.pi * np.arange(s[0] // 2 + 1) / s[0])
    w1.imag = np.sin(np.pi * np.arange(s[0] // 2 + 1) / s[0])
    w2 = np.empty(s[1] // 2 + 1, complex)
    w2.real = np.cos(np.pi * np.arange(s[1] // 2 + 1) / s[1])
    w2.imag = np.sin(np.pi * np.arange(s[1] // 2 + 1) / s[1])

    return w1[:, None] * X[:s[0] // 2 + 1, :s[1] // 2 + 1] * w2

def ihfft2(x, s=None):
    """Compute the inverse of hfft2"""
    x = np.asarray(x, dtype=complex)
    if s is None:
        s = [n * 2 - 2 for n in x.shape]

    # build the weight vectors
    w1 = np.empty(s[0] // 2 + 1, complex)
    w1.real = np.cos(np.pi * np.arange(s[0] // 2 + 1) / s[0])
    w1.imag = np.sin(np.pi * np.arange(s[0] // 2 + 1) / s[0])
    w2 = np.empty(s[1] // 2 + 1, complex)
    w2.real = np.cos(np.pi * np.arange(s[1] // 2 + 1) / s[1])
    w2.imag = np.sin(np.pi * np.arange(s[1] // 2 + 1) / s[1])

    X = np.empty(s, complex)
    X[:s[0] // 2 + 1, :s[1] // 2 + 1] = x * w1[:, None] * w2
    X[s[0] // 2 + 1:, :s[1] // 2 + 1] = x[-2:0:-1, :].conj() * w1[1:-1, None] * w2
    X[:s[0] // 2 + 1, s[1] // 2 + 1:] = x[:, -2:0:-1].conj() * w1[:, None] * w2[1:-1]
    X[s[0] // 2 + 1:, s[1] // 2 + 1:] = x[-2:0:-1, -2:0:-1] * w1[1:-1, None] * w2[1:-1]

    return ifft2(X).real

def hfftn(x, s=None, axes=None):
    """Compute the N-D discrete Fourier Transform for Hermitian-symmetric input"""
    x = np.asarray(x, dtype=float)
    if s is None:
        s = x.shape
    if axes is None:
        axes = range(x.ndim)
    for k in axes:
        if s[k] < x.shape[k]:
            raise ValueError("s = %s is less than x.shape = %s" % (s, x.shape))
        elif s[k] > x.shape[k]:
            x = np.resize(x, s)

    # Perform an O[N log N] complex-to-complex FFT
    X = fftn(x, axes=axes)

    # build the weight vectors
    w = []
    for k in axes:
        w.append(np.empty(s[k] // 2 + 1, complex))
        w[-1].real = np.cos(np.pi * np.arange(s[k] // 2 + 1) / s[k])
        w[-1].imag = np.sin(np.pi * np.arange(s[k] // 2 + 1) / s[k])

    # multiply the appropriate slices of X by the weights
    for k in axes:
        sl = [slice(None)] * x.ndim
        sl[k] = slice(None, s[k] // 2 + 1)
        X[tuple(sl)] *= w[k]

    return X

def ihfftn(x, s=None, axes=None):
    """Compute the inverse of hfftn"""
    x = np.asarray(x, dtype=complex)
    if s is None:
        s = [n * 2 - 2 for n in x.shape]
    if axes is None:
        axes = range(x.ndim)

    # build the weight vectors
    w = []
    for k in axes:
        w.append(np.empty(s[k] // 2 + 1, complex))
        w[-1].real = np.cos(np.pi * np.arange(s[k] // 2 + 1) / s[k])
        w[-1].imag = np.sin(np.pi * np.arange(s[k] // 2 + 1) / s[k])

    # multiply the appropriate slices of X by the weights
    X = np.empty(s, complex)
    for k in axes:
        sl = [slice(None)] * x.ndim
        sl[k] = slice(None, s[k] // 2 + 1)
        X[tuple(sl)] = x[tuple(sl)] * w[k]

    # build the slices for the negative frequencies
    slices = []
    for k in axes:
        sl = [slice(None)] * x.ndim
        sl[k] = slice(s[k] // 2 + 1, None)
        slices.append(tuple(sl))

    # copy the appropriate slices of X
    for k in range(len(axes)):
        sl = slices[k]
        X[sl] = x[slices[k - 1]].conj()

    return ifftn(X, axes=axes).real

def hfft(x, s=None, axis=-1):
    """Compute the 1-D discrete Fourier Transform for Hermitian-symmetric input"""
    x = np.asarray(x, dtype=float)
    if s is None:
        s = x.shape[axis]
    if s < x.shape[axis]:
        raise ValueError("s = %s is less than x.shape = %s" % (s, x.shape))
    elif s > x.shape[axis]:
        x = np.resize(x, s)

    # Perform an O[N log N] complex-to-complex FFT
    X = fft(x)

    # build the weight vectors
    w = np.empty(s // 2 + 1, complex)
    w.real = np.cos(np.pi * np.arange(s // 2 + 1) / s)
    w.imag = np.sin(np.pi * np.arange(s // 2 + 1) / s)

    return w * X[:s // 2 + 1]

def ihfft(x, s=None, axis=-1):
    """Compute the inverse of hfft"""
    x = np.asarray(x, dtype=complex)
    if s is None:
        s = 2 * (x.shape[axis] - 1)
    if s < x.shape[axis]:
        raise ValueError("s = %s is less than x.shape = %s" % (s, x.shape))

    # build the weight vectors
    w = np.empty(s // 2 + 1, complex)
    w.real = np.cos(np.pi * np.arange(s // 2 + 1) / s)
    w.imag = np.sin(np.pi * np.arange(s // 2 + 1) / s)

    X = np.empty(s, complex)
    X[:s // 2 + 1] = x * w
    X[s // 2 + 1:] = x[-2:0:-1].conj() * w[1:-1]

    return ifft(X).real

def hfftfreq(n, d=1.0):
    """Return the Discrete Fourier Transform sample frequencies for Hermitian-symmetric input"""
    if not isinstance(n, int) or n < 1:
        raise ValueError("n = %s is not a positive integer" % n)
    val = 1.0 / (n * d)
    N = n // 2 + 1
    results = np.arange(0, N, dtype=int)
    return results * val

def hfftshift(x, n=None):
    """Shift the zero-frequency component to the center of the spectrum for Hermitian-symmetric input"""
    x = np.asarray(x)
    if n is None:
        n = x.ndim
    if n > x.ndim:
        raise ValueError("n = %s is greater than x.ndim = %s" % (n, x.ndim))
    for k in range(n):
        m = x.shape[k] // 2
        x = np.roll(x, m, k)
    return x

def ihfftshift(x, n=None):
    """Shift the zero-frequency component to the center of the spectrum for Hermitian-symmetric input"""
    x = np.asarray(x)
    if n is None:
        n = x.ndim
    if n > x.ndim:
        raise ValueError("n = %s is greater than x.ndim = %s" % (n, x.ndim))
    for k in range(n):
        m = (x.shape[k] + 1) // 2
        x = np.roll(x, m, k)
    return x

def hfftn(x, s=None, axes=None):
    """Compute the n-D discrete Fourier Transform for Hermitian-symmetric input"""
    x = np.asarray(x, dtype=float)
    if s is None:
        s = [n for n in x.shape]
    if axes is None:
        axes = range(x.ndim)

    # Perform an O[N log N] complex-to-complex FFT
    X = fftn(x)

    # build the weight vectors
    w = []
    for k in axes:
        w.append(np.empty(s[k] // 2 + 1, complex))
        w[-1].real = np.cos(np.pi * np.arange(s[k] // 2 + 1) / s[k])
        w[-1].imag = np.sin(np.pi * np.arange(s[k] // 2 + 1) / s[k])

    # multiply the appropriate slices of X by the weights
    for k in axes:
        sl = [slice(None)] * x.ndim
        sl[k] = slice(None, s[k] // 2 + 1)
        X[tuple(sl)] *= w[k]

    return X

def ihfftn(x, s=None, axes=None):
    """Compute the inverse of hfftn"""
    x = np.asarray(x, dtype=complex)
    if s is None:
        s = [2 * (n - 1) for n in x.shape]
    if axes is None:
        axes = range(x.ndim)

    # build the weight vectors
    w = []
    for k in axes:
        w.append(np.empty(s[k] // 2 + 1, complex))
        w[-1].real = np.cos(np.pi * np.arange(s[k] // 2 + 1) / s[k])
        w[-1].imag = np.sin(np.pi * np.arange(s[k] // 2 + 1) / s[k])

    # multiply the appropriate slices of X by the weights
    X = np.empty(s, complex)
    for k in axes:
        sl = [slice(None)] * x.ndim
        sl[k] = slice(None, s[k] // 2 + 1)
        X[tuple(sl)] = x[tuple(sl)] * w[k]

    # build the slices for the negative frequencies
    slices = []
    for k in axes:
        sl = [slice(None)] * x.ndim
        sl[k] = slice(s[k] // 2 + 1, None)
        slices.append(tuple(sl))

    # copy the appropriate slices of X
    for k in range(len(axes)):
        sl = slices[k]
        X[sl] = x[slices[k - 1]].conj()

    return ifftn(X, axes=axes).real

def hfft2(x, s=None, axes=(-2, -1)):
    """Compute the 2-D discrete Fourier Transform for Hermitian-symmetric input"""
    return hfftn(x, s=s, axes=axes)

def ifftn(x, s=None, axes=None):
    """Compute the n-D inverse discrete Fourier Transform"""
    x = np.asarray(x, dtype=complex)
    if s is None:
        s = x.shape
    if axes is None:
        axes = range(x.ndim)

    # Perform an O[N log N] complex-to-complex FFT
    X = fftn(x)

    # build the weight vectors
    w = []
    for k in axes:
        w.append(np.empty(s[k], complex))
        w[-1].real = np.cos(2 * np.pi * np.arange(s[k]) / s[k])
        w[-1].imag = np.sin(2 * np.pi * np.arange(s[k]) / s[k])

    # multiply the appropriate slices of X by the weights
    for k in axes:
        sl = [slice(None)] * x.ndim
        sl[k] = slice(None)
        X[tuple(sl)] *= w[k]

    return X

def fftn(x, s=None, axes=None):
    """Compute the n-D discrete Fourier Transform"""
    x = np.asarray(x, dtype=float)
    if s is None:
        s = x.shape
    if axes is None:
        axes = range(x.ndim)

    # Perform an O[N log N] complex-to-complex FFT
    X = fftn(x)

    # build the weight vectors
    w = []
    for k in axes:
        w.append(np.empty(s[k], complex))
        w[-1].real = np.cos(2 * np.pi * np.arange(s[k]) / s[k])
        w[-1].imag = np.sin(2 * np.pi * np.arange(s[k]) / s[k])

    # multiply the appropriate slices of X by the weights
    for k in axes:
        sl = [slice(None)] * x.ndim
        sl[k] = slice(None)
        X[tuple(sl)] *= w[k]

    return X

def test():
    x = np.random.rand(4, 4)
    X = hfft2(x)
    x2 = ihfft2(X)
    print(np.allclose(x, x2))
    

test()