import logging

class Prime(object):
    """
    We maintain two pieces of state: a list and a set.
    The set (known_primes) contains all known primes, in no order and not necessarily contiguous.
    These are used to do a look-up to short-circuit checks of primality.
    The list (known_primes_contiguous) is used to check for numbers that are not yet known to be prime or composite.
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
        

    def iter_primes(self, max_value=None, max_num=None, start_num=None):
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
        
        >>> [i for i in p.iter_primes(max_num=3)]
        [2, 3, 5]
        >>> [i for i in p.iter_primes(max_num=10)]
        [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        
        >>> [i for i in p.iter_primes(max_num=10, start_num=7)]
        [19, 23, 29]
        """
        ii = start_num or 0
        if ii > len(self.known_primes_contiguous):
            raise NotImplementedError('cannot start beyond contiguous known primes (currently {:d} of them)'.format(
            len(self.known_primes_contiguous)))
            
        def _finished(c, ii=None):
            return ((max_value is not None) and (c > max_value) or 
                    ((max_num is not None) and (ii is not None) and (ii >= max_num)))
        c = 1
        while not _finished(c, ii):
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
    
    def prime_factors(self, n):
        """
        Recursive.
        
        >>> p = Prime()
        >>> p.prime_factors(9)
        [3, 3]
        >>> p.prime_factors(21)
        [3, 7]
        >>> p.prime_factors(51)
        [3, 17]
        >>> p.prime_factors(53)
        [53]
        >>> p.prime_factors(1021)
        [1021]
        """
        f = []
        for p in self.iter_primes(n**(1/2)):
            if n%p == 0:
                f += [p]
                f += self.prime_factors(n//p)
                break
        if len(f) == 0:
            f += [n]
        return f
    
    def are_prime(self, candidates):
        """
        >>> p = Prime()
        >>> p.are_prime([2, 3, 5])
        True
        >>> p.are_prime([2, 3, 5, 6])
        False
        
        """
        found = False
        for c in candidates:
            if not self.is_prime(c):
                found = True
        return not found
        
    def load(self, fname='known_primes_contiguous.txt', verify=1000, load_smaller=False):
        kpc = []
        with open(fname, 'rt') as f:
            kpc = [int(i) for i in f.readlines()]
        if verify and not self.are_prime(kpc[0:verify]):
            raise ValueError('first {:d} loaded numbers are not prime'.format(verify_num))
        if len(self.known_primes_contiguous) > len(kpc):
            if not load_smaller:
                raise ValueError('{:d} primes loaded, but already have {:d}'.format(
                    len(kpc),
                    len(self.known_primes_contiguous)))
        self.__known_primes = set()
        self.known_primes_contiguous = kpc

    def save(self, fname=None, overwrite=False):
        if fname is None:
            fname = 'known_primes_contiguous.txt'
        bytes_written = None
        with open(fname, 'w' if overwrite else 'x') as f:
            bytes_written = f.write('\n'.join([str(p) for p in self.known_primes_contiguous]))
        return bytes_written
    
if __name__ == '__main__':
    import doctest
    doctest.testmod()