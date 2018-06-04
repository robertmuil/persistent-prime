import logging

class Prime(object):
    """
    We maintain two pieces of state: a list and a set.
    The set (known_primes) contains all known primes, in no order and not necessarily contiguous.
    These 
    """
    def __init__(self):
        self.__known_primes = set()
        self.known_primes_contiguous = [2, 3, 5, 7, 11]
        self.lg = logging.getLogger(__name__)
        self.lg.info('Prime.__init__()')
        
    @property
    def known_primes(self):
        return self.__known_primes
    
    @known_primes.setter
    def known_primes(self, kp):
        self.__known_primes = set(kp)
        
    def _add_known_prime(self, p):
        if p not in self.__known_primes:
            self.__known_primes = self.__known_primes.union({p})
    
    @property
    def known_primes_contiguous(self):
        return self.__known_primes_contiguous
    
    @known_primes_contiguous.setter
    def known_primes_contiguous(self, kpc):
        self.__known_primes_contiguous = kpc
        self.__known_primes = self.__known_primes.union(kpc)
        
    def prime_factors_known(self, n):
        """
        Recursive
        """
        f = []
        if n > self.known_primes_contiguous[-1]**2:
            raise ValueError('n too high for current known_primes')
        for p in self.known_primes_contiguous:
            if n%p == 0:
                f += [p]
                f += self.prime_factors_known(n/p)
                break
        if len(f) == 0:
            f += [n]
        return f
    
    def iter_primes(self, max_value=None):
        """
        Iterates over *all* prime numbers, utilising the known_primes first.
        
        Together with is_prime() this is recursive.
        
        >>> p = Prime()
        >>> [i for i in p.iter_primes(10)]
        [2, 3, 5, 7]
        >>> [i for i in p.iter_primes(20)]
        [2, 3, 5, 7, 11, 13, 17, 19]
        >>> [i for i in p.iter_primes(3)]
        [2, 3]
        """
        ii = 0
        def _finished(c):
            return (max_value is not None) and (c > max_value)
        c = 1
        while not _finished(c):
            while ii+1 > len(self.known_primes_contiguous):
                c = self.known_primes_contiguous[-1] + 2
                if _finished(c):
                    return
                while not self.is_prime(c):
                    c += 2
                    if _finished(c):
                        return
                self.known_primes_contiguous += [c]
            next_p = self.known_primes_contiguous[ii]
            if _finished(next_p):
                return
            ii += 1
            yield next_p
    
    def is_prime(self, n):
        """
        Beyond known_primes, this and iter_primes form a recursive group.
        
        >>> p = Prime()
        >>> p.is_prime(119)
        False
        >>> p.is_prime(121)
        False
        >>> p.is_prime(149)
        True
        >>> p.is_prime(1021)
        True
        
        """
        rv = None
        
        if n in self.known_primes:
            rv = True
        else:
            for p in self.iter_primes():
                if n%p == 0:
                    self.lg.info('found prime factor: {:d}'.format(p))
                    rv = False
                    break
                if p**2 > n:
                    self.lg.debug('p**2>n')
                    self._add_known_prime(n)
                    rv = True
                    break   
        
        return rv
    
if __name__ == '__main__':
    import doctest
    doctest.testmod()