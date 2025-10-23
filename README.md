# csc410-lab2

Notes:

Maximum network bandwidth: 987 Mbits/sec


Test Specs:

Original -> 700, .05
Heavier -> 1000, .035
Lighter -> 500, .07

TO DO:

For each test (tests 1, 2, 3, 4, and 5 for each of the three setups):

    Look at the httperf output file, and the corresponding file for CPU utilization and for disk utilization.

    In the httperf output, compare the "connect" time to the "reply" time. When he was showing us in class, the connect time was a lot higher than the reply time which means something is off, but we don't know what yet.

    Determine if there is a hardware bottleneck. To do this, check for abnormally high (or low?) values in CPU utilization, disk utilization, and network utilization. The CPU and disk values are in the corresponding files. I think for CPU, look out for 100% or 0%, and for disk look out for closer to 100% ? For the network utilization, compare the "Net I/O" value in the httperf output with the maximum network bandwidth (987 Mbits/sec).

