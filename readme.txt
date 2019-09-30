This python manuscript file_randomness.py is a tool to measure the randomness in a file
with Shannon Entropy. It takes O(1) space and O(n) time. It should work under both python 2 and 3.

To use it, the simplest way is
  "python file_randomness.py path_to_target_file"

It will detect the subsections with high randomness in a file when the -d flag is added
  "python file_randomness.py -d path_to_target_file"

It on default calculate the entropy at the byte level, but one can change that with the -b argument
It on default uses 2 as the base in logarithm, but one can change it with the -l argument
For more information, please refer to the help message using -h flag
  "python file_randomness.py -h"

Detection of the subsections with high randomness is performed at the chunk level (by default it is 4KB),
with preset thresholds.

If allowing a 3rd party library, I think a package that can detect the encoding of a text file can be
useful here as it can help to provide more information on the symbols.

I think in general entropy gives a good estimation on the randomness of a file, however it is not a consistent
measurement: a larger file usually provides larger entropy than a smaller file with similar randomness.
That's its pitfall.


Below are some of the tests I ran.
i) For plain English texts (shakespeare.txt), it reported an entropy of ~4.6 out of 8.
ii) When the text is encrypted (shakespeare.zip), the entropy reached a very high level.
iii) For plain Chinese texts (chinese.txt), it reported a high entropy, ~5.8
iv) A Binary file (ripgrep_0.10.0_amd64.deb) also comes with high randomness
v) For a "hybrid" format such as pdf, some of the subsections are reported to be with high-randomness






➜  python file_randomness.py test_files/shakespeare.txt
Input file path: test_files/shakespeare.txt
File Size: 5458199 bytes
------
The randomness of this file is: 4.6017 (out of 8.0, measured by entropy)

➜  python file_randomness.py test_files/shakespeare.zip
Input file path: test_files/shakespeare.zip
File Size: 2024265 bytes
------
The randomness of this file is: 7.9990 (out of 8.0, measured by entropy)

➜  python file_randomness.py test_files/chinese.txt
Input file path: test_files/chinese.txt
File Size: 919380 bytes
------
The randomness of this file is: 5.8408 (out of 8.0, measured by entropy)

➜  python file_randomness.py -b 16 test_files/chinese.txt
Input file path: test_files/chinese.txt
File Size: 919380 bytes
------
The randomness of this file is: 9.3508 (out of 16.0, measured by entropy)

➜  python file_randomness.py -b 16 -l e test_files/chinese.txt
Input file path: test_files/chinese.txt
File Size: 919380 bytes
------
The randomness of this file is: 6.4815 (out of 11.1, measured by entropy)

➜  python file_randomness.py test_files/ripgrep_0.10.0_amd64.deb
Input file path: test_files/ripgrep_0.10.0_amd64.deb
File Size: 1461290 bytes
------
The randomness of this file is: 7.9999 (out of 8.0, measured by entropy)

➜  python file_randomness.py test_files/hacking.jpg
Input file path: test_files/hacking.jpg
File Size: 360530 bytes
------
The randomness of this file is: 7.9609 (out of 8.0, measured by entropy)

➜  python file_randomness.py -d test_files/Raspberry-Pi-Cookbook-for-Python-Programmers.pdf
Input file path: test_files/Raspberry-Pi-Cookbook-for-Python-Programmers.pdf
File Size: 32019434 bytes
------
The randomness of this file is: 4.5992 (out of 8.0, measured by entropy)
------
Detecting subsections with high randomness
High randomness subsection starts at 23699456 bytes, ends at 23707648 bytes
High randomness subsection starts at 23711744 bytes, ends at 23773184 bytes
High randomness subsection starts at 23785472 bytes, ends at 23793664 bytes
High randomness subsection starts at 23801856 bytes, ends at 23822336 bytes
High randomness subsection starts at 23834624 bytes, ends at 24506368 bytes
High randomness subsection starts at 24510464 bytes, ends at 24707072 bytes
High randomness subsection starts at 24711168 bytes, ends at 25616384 bytes
High randomness subsection starts at 25620480 bytes, ends at 26615808 bytes
High randomness subsection starts at 26619904 bytes, ends at 26726400 bytes
High randomness subsection starts at 26730496 bytes, ends at 26800128 bytes
High randomness subsection starts at 26804224 bytes, ends at 27533312 bytes
High randomness subsection starts at 27537408 bytes, ends at 27594752 bytes
High randomness subsection starts at 27598848 bytes, ends at 28426240 bytes
High randomness subsection starts at 28430336 bytes, ends at 29388800 bytes
High randomness subsection starts at 29392896 bytes, ends at 29618176 bytes
High randomness subsection starts at 29622272 bytes, ends at 31068160 bytes
High randomness subsection starts at 31092736 bytes, ends at 31322112 bytes
Detection ended
------

