#!/usr/bin/env python
# coding: utf-8

"""
Memoized

Module that provides a decorator to cache function calls.
"""

import os
import time
import functools
try:
    import cPickle as pickle
except ImportError:
    import pickle


class Memoized(object):
    """
    Decorator that caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned, and
    not re-evaluated.

    The content of cache it's loadead and saved on a pickle file.
    """

    cache_dir = '/tmp/'
    lifetime = 60 * 60 * 6
    __cache__ = None

    @classmethod
    def set_cache_dir(self, cache_dir):
        """
        setup cache directory
        default: /tmp/
        """
        self.cache_dir = cache_dir

    @classmethod
    def set_lifetime(self, lifetime):
        """
        setup lifetime
        default: 216006 (6 minutes)
        """
        self.lifetime = lifetime

    def __init__(self, func):
        self.func = func
        self.cache_file = '_cached_' + self.func.__name__

    @property
    def cache(self):
        """
        Open and unpickle the cache file or returns an empty dict if it fail
        """
        if self.__cache__ == None:
            try:
                with open(self.cache_dir + os.sep + self.cache_file) as fd:
                    self.__cache__ = pickle.load(fd)
            except Exception, error:
                self.__cache__ = {}
        return self.__cache__

    def __call__(self, *args, **kwargs):
        """
        Decorator function
        """
        try:
            # dont want to use "self" as key
            #key = str(args[1:]) + str(kwargs)
            key = str(args) + str(kwargs)
            time_key = key + '_time'

            if key not in self.cache or \
                 self.cache[time_key] < time.time() - self.lifetime:

                value = self.func(*args, **kwargs)
                self.cache[key] = value
                self.cache[time_key] = time.time()
                with open(self.cache_dir + os.sep + self.cache_file, 'w') as fd:
                    pickle.dump(self.cache, fd)
                return value
        except TypeError:
            # uncachable -- for instance, passing a list as an argument.
            # Better to not cache than to blow up entirely.
            return self.func(*args, **kwargs)

        return self.cache[key]

    def __repr__(self):
        """
        Return the function's docstring.
        """

        return self.func.__doc__

    def __get__(self, obj, objtype):
        """
        Support instance methods.
        """

        return functools.partial(self.__call__, obj)
