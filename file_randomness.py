#!/usr/bin/env python
# -*- encoding: utf8 -*-

'''
file_randomness.py

Measure the randomness of a file with Shannon Entropy

usage: python file_randomness.py [-h] [-b BITS_PER_SYMBOL] [-l LOG_BASE] [-d]
                                 file_path

positional arguments:
  file_path             The path to target file

optional arguments:
  -h, --help            show this help message and exit
  -b BITS_PER_SYMBOL, --bits_per_symbol BITS_PER_SYMBOL
                        Number of bits in each symbols, default value is 8,
                        i.e. 1 byte.Only 4, 8, 16 bits are allowed
  -l LOG_BASE, --log_base LOG_BASE
                        The base of the logarithm in calculating the entropy,
                        default value is 2
  -d, --detect_anomaly  Add this flag if you want to detect high-random
                        subsections

It should work under python2 and python3
'''


from __future__ import print_function
import os
import math
import sys
import argparse


class randomness(object):
    '''
    Calculate the shannon entropy of a file.

    '''
    # When measuring entropy, the size of the base elements (symbols)
    _bits_per_symbol = 8  # bits
    # chunk size when reading files, on default, it is 4KB
    # This is used to avoid loading the whole file into memory
    _read_chunk_size = 4096
    _log_base = 2
    # These two values are used to determine whether the chunk is of high-randomness
    # For now I mannual set the values based on my observation
    # It definitely worth looking into literatures for more accurate thresholds
    _high_randomness_threshold_abs = 6
    _high_randomness_threshold_ratio = 1.25
    
    # _possible_symbols = 2 ** _bits_per_symbol
    def __init__(self, args):
        
        self.filename = args['filename']
        self._check_input_file()
        
        if 'bits_per_symbol' in args:
            if args_ns.bits_per_symbol not in ('4', '8', '16'):
                print('For now, we only allow calculating entropy based on ' +
                      '4-bit, 8-bit and 16-bit symbols,', end=' ')
                print('Switching back to 8-bit')
                self._set_bits_per_symbol(self._bits_per_symbol)
            else:
                self._set_bits_per_symbol(int(args['bits_per_symbol']))
        else:
            self._set_bits_per_symbol(self._bits_per_symbol)
        
        if 'log_base' in args:
            if args['log_base'] == 'e':
                self._log_base = math.e
            else:
                try:
                    self._log_base = int(args_ns.log_base)
                except ValueError:
                    print('Please choose a valid base for logarithm,', end=' ')
                    print('Switching back to 2')
                    self._log_base = 2
            if self._log_base < 2:
                print('Please choose a valid base for logarithm,', end=' ')
                print('Switching back to 2')
                self._log_base = 2
        
        if 'detect' in args:
            self.detect = True
            if self._bits_per_symbol != 8:
                print('For now, it only supports byte-level' +
                      'high-randomness subsection detection,', end=' ')
                print('Switching back to 8 bits per symbol')
                self._set_bits_per_symbol(8)
        else:
            self.detect = False


    def calculate(self):
        '''
        Measure the file randomness by Shannon Entropy.

        '''
        self.entropy()

        if self.detect:
            # Detecting high-randomness subsections
            self.detect_anomaly()
        

    def _set_bits_per_symbol(self, val):
        '''
        Setting up a few attributes related to bits per symbol.

        By default, val is 8, meaning that we only consider entropy
        at the byte level.
        However, in cerntain encodings, different number of bits are used
        in one symbol.
        '''
        self._bits_per_symbol = val
        self._symbol_pool_size = 2 ** self._bits_per_symbol  # total number of possible symbols
        if self._bits_per_symbol == 8:
            self._total_symbol_count = self.filesize  # total number of symbols in one file
        elif self._bits_per_symbol == 4:
            self._total_symbol_count = self.filesize * 2
        else:
            self._total_symbol_count = self.filesize // 2


    def _check_input_file(self):
        '''
        Check whether the input file is valid.

        '''

        print('Input file path: %s' % self.filename)
        if not os.path.isfile(self.filename):
            # If file does not exist
            print('Please make sure you typed in the correct path for the input file')
            exit(0)

        # Get the file size with os library
        self.filesize = os.stat(self.filename).st_size
        print('File Size: %d bytes' % self.filesize)
        
        try:
            with open(self.filename, 'rb') as fp:
                fp.read(1)
        except PermissionError:
            # If current user doesn't have permission to read the file
            print('Please make sure you have permission to access the input file')
            exit(0)
        
        
    def entropy(self):
        '''
        Calculate the file entropy (Shannon Entropy).

        H = - sum p_i log_2(p_i)
        where p_i is the relative frequency (probability) of a certain symbol in
        the input file
        '''
        
        chars = [0] * self._symbol_pool_size  # Used for storing frequency

        with open(self.filename, 'rb') as fp:
            while True:
                # Each time, read a chunk with a size of self._read_chunk_size bytes
                chunk_content = fp.read(self._read_chunk_size)
                if sys.version_info < (3, 0):
                    # handing the impactability between python2 and python3
                    chunk_content = map(ord, chunk_content)
                if not chunk_content:
                    # When reaches the end of the file
                    fp.close()
                    break

                if self._bits_per_symbol == 8:
                    # If we are considering 8-bit symbols (default)
                    for c in chunk_content:
                        chars[c] += 1
                elif self._bits_per_symbol == 4:
                    # If we are considering 4-bit symbols
                    for c in chunk_content:
                        chars[c % 16] += 1
                        chars[c // 16] += 1
                elif self._bits_per_symbol == 16:
                    # If we are considering 16-bit symbols
                    for c1, c2 in zip(chunk_content[::2], chunk_content[1::2]):
                        chars[c1 * 256 + c2] += 1
        
        # Entropy:  H = - \sum p_i \log_2(p_i)
        self.entropy = - sum((1. * chars[i] / self._total_symbol_count) *
                             math.log(1. * chars[i] / self._total_symbol_count,
                                      self._log_base)
                             for i in range(self._symbol_pool_size) if chars[i])
        # The maximum possible entropy under the give bits_per_symbol
        self.max_entropy = - sum(1./self._symbol_pool_size * 
                                math.log(1./self._symbol_pool_size, self._log_base)
                                for i in range(self._symbol_pool_size))

        print('------')
        print('The randomness of this file is: %.4f (out of %.1f, measured by entropy)'
              % (self.entropy, self.max_entropy))
        return self.entropy
    
    
    def detect_anomaly(self):
        '''
        Detection of the high-randomness subsections.

        Detection is performed at the chunk level
        If the entropy surpasses certain threshold, I consider it to be a subsection
        with high randomness 
        '''
        # used to determine the start and end of a high-randomness subsection
        high_randomness_flag = False
        read_chunk_count = 0
        print('------\nDetecting subsections with high randomness')
        with open(self.filename, 'rb') as fp:
            while True:
                chars = [0] * self._symbol_pool_size
                # Each time, read a chunk with a size of self._read_chunk_size bytes
                chunk_content = fp.read(self._read_chunk_size)
                if sys.version_info < (3, 0):
                    chunk_content = map(ord, chunk_content)
                if not chunk_content:
                    # When reaches the end of the file
                    fp.close()
                    break
                for c in chunk_content:
                    chars[c] += 1
        
                # Calculate the entropy of current chunk
                chunk_entropy = - sum((1. * chars[i] / self._read_chunk_size) *
                                      math.log(1. * chars[i] / self._read_chunk_size,
                                               self._log_base)
                                      for i in range(self._symbol_pool_size) if chars[i])

                # If the entropy surpasses 6 or if it is above 1.25 times the average entropy level
                # I consider it to be a subsection with high-randomness
                # When output once for continuous subsection
                if chunk_entropy > min(self.entropy * self._high_randomness_threshold_ratio,
                                       self._high_randomness_threshold_abs):
                    if high_randomness_flag == False:
                        start_byte = read_chunk_count * self._read_chunk_size
                        print('High randomness subsection starts at %d bytes, ' % start_byte,
                              end='')
                        high_randomness_flag = True
                else:
                    if high_randomness_flag == True:
                        end_byte = min(read_chunk_count * self._read_chunk_size, self.filesize)
                        print('ends at %d bytes' % end_byte)
                        high_randomness_flag = False
                read_chunk_count += 1
        if high_randomness_flag == True:
            print('High-randomness subsection ends at %d bytes' % self.filesize)

        print('Detection ended\n------')


if __name__ == "__main__":
    '''
    Parse the arguments, one can simply type
    python file_randomness.py -h
    for help message
    '''
    parser = argparse.ArgumentParser(add_help=True,
                        description='Measure the randomness of a file with Shannon Entropy')
    parser.add_argument("file_path",
                        action='store', default='',
                        help='The path to target file')
    parser.add_argument('-b', '--bits_per_symbol',
                        action="store", dest="bits_per_symbol", default=0,
                        help=('Number of bits in each symbols, default value is 8, i.e. 1 byte.'+
                              'Only 4, 8, 16 bits are allowed')
                       )
    parser.add_argument('-l', '--log_base',
                        action="store", dest="log_base", default=0,
                        help=('The base of the logarithm in calculating the entropy,' + 
                              'default value is 2'))
    parser.add_argument('-d', '--detect_anomaly',
                        action="store_true", dest='detect', default=False,
                        help='Add this flag if you want to detect high-random subsections')
    args_ns = parser.parse_args()
    args = {}
    if args_ns.file_path:
        args['filename'] = args_ns.file_path
    if args_ns.bits_per_symbol:
        args['bits_per_symbol'] = args_ns.bits_per_symbol
    if args_ns.log_base:
        args['log_base'] = args_ns.log_base
    if args_ns.detect:
        args['detect'] = True

    target = randomness(args)
    target.calculate()
