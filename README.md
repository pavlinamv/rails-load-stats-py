rails-load-stats.py and candlepin-load-stats.py scripts for creating statistics. Both scripts work quite similarly.

## rails-load-stats.py

rails-load-stats.py is [rails-load-stats script](https://github.com/pmoravec/rails-load-stats) writen in Python. Similarly as [rails-load-stats script](https://github.com/pmoravec/rails-load-stats) it processes a logfile of a Ruby on Rails app to analyze where the load to the app comes from.  Similarly as [rails-load-stats script](https://github.com/pmoravec/rails-load-stats) it produces statistics about:
- Particular requests: how many requests against each method were raised, how much (min/max/avg/sum) time these took, and what percentage of overall execution time was spent by processing the different types of requests.
- Maximal level of concurrency: the peak number of requests that were processed in parallel.

rails-load-stats-py is faster than the original bash version (especially for larger logfiles) and it contains some new features:
- list of particular requests from the most busy time (processed with the most concurrency)
- if "--with_stats" option is used, it creates directory "`stats` + name of the input file" and for each request type it creates two files in the directory:
    - plot with the times of all requests of the type (sorted by the timestamp of the request)
    - text file containing the time of the request and its unique id (sorted by the size of time spent on the request)
    

## Usage: 
    rails-load-stats <FILE> [SORTING_TYPE] [--with_stats]
    candlepin-load-stats <FILE> [SORTING_TYPE] [--with_stats]

        Possible sorting types are:
            1 or 'name': sort by the request_type
            2 or 'count': sort by the count
            3 or 'min': sort by the min time
            4 or 'max': sort by the max time
            5 or 'avg': sort by the avg time
            6 or 'mean': sort by the mean time
            7 or 8 or 'percentage': sort by the sum time / percentage


Example of usage:

    [localhost]$ ./rails-load-stats.py test.log --with_stats
    
    Extracting data from the input file.
    |███████████████████████████████| 100.0 %  Estimated time left: 1 sec       
    there were 10 requests taking 1181 ms (i.e. 0.00 hours, i.e. 0.00 days) in summary

        request_type                      count    min    max  -  max_id       avg    mean    sum    percentage
    --  ------------------------------  -------  -----  -----  ------------  -----  ------  -----  ------------
     1  PuppetcaController#index              5     94    357  - '2ac5eab2'    198     184    993         84.08
     2  HostsController#index                 2     25     34  - '7aa5aeb2'     29      29     59          5
     3  HostsController#externalNodes         1     57     57  - '980ab765'     57      57     57          4.83
     4  CandlepinProxiesController#get        1     38     38  - '7d3b40e6'     38      38     38          3.22
     5  UsersController#login                 1     34     34  - '7d3b40e3'     34      34     34          2.88
    
    Maximally 3 concurrent requests when processing:
      Number  Time                 Request ID    Endpoint
    --------  -------------------  ------------  ---------------------
           0  2023-01-10T03:46:26  2ac9eab0      HostsController#index
           1  2023-01-10T03:46:26  7aa5aeb2      HostsController#index
           2  2023-01-10T03:46:26  2ac5eab0      HostsController#index

    1 processing requests are not closed in the end of file:
      Number     Pending time (s)  Time stamp           Request    IDEndpoint
    --------  -------------------  -------------------  ---------  ---------------------
           1                    0  2023-01-10T03:46:26  2ac5eab0   HostsController#index

Now we can see the list of identificators + times spent on the request for any type of request. Request `PuppetcaController#index` (1st line in the previous table) is in `data_1.txt`, `HostsController#index` (2nd line) is in `data_2.txt`, ... 

    [localhost]$ more stats_test.log/data_001.txt 
    PuppetcaController#index
    ------------------------
    
    Table of 'PuppetcaController#index' requests duration and its corresponding uniq
    ue ID. The table is sorted by the size of duration in ascending order. 
    
    duration    request ID
    ----------  --------------------------------
         357     2ac5eab2
         201     2ac5eab5
         184     2ac5eab3
         157     2ac5eab1
          94     2ac5eab4


Corresponding `.png` file for `PuppetcaController#index` is in `plot_2.png`. In the file times spent on the request is depicted according to time order of the requests.

    [locahost]$ gimp stats_test.log/plot_001.txt

![plot_001](https://github.com/pavlinamv/rails-load-stats-py/assets/22654167/05484dae-1d45-48f5-b500-0f3c0b8dba89)


## Requirements:
Python version >= 3.6

tabulate - library for printing tables

mathplotlib - library for creating plots (if --with_stats is used)


## candlepin-load-stats.py

candlepin-load-stats.py is similar as rails-load-stats.py script. It processes a candlepin logfile to analyze where the load to the app comes from. It works the same as rails-load-stats.py, and have the same usage and requirements.

Example output:

    there were 149084 requests taking 2137814 ms (i.e. 0.59 hours, i.e. 0.02 days) in summary

    action: request_type                               count    min    max  -  max_id     avg    mean    sum    percentage
    --  --------------------------------------------  -------  -----  -----  ---------  ------  -----  -------  ------------
    1  GET  :/candlepin/cons/UUID/certificates         25856      5   1714  - 'aeadff82'   23      14   594799       27.82
    2  GET  :/candlepin/cons/UUID                      16071      3    787  - '2cf45a69'   28      19   462696       21.64
    3  GET  :/candlepin/cons/UUID/content_overrides    34666      3    376  - '254dcb99 '   9       6   316487       14.8
    4  GET  :/candlepin/cons/UUID/accessible_content   16034      4    389  - '9089b687'   14       9   227700       10.65
    ...
    ...

    Maximally 2 concurrent requests when processing:
    id                                    action    request_type
    ------------------------------------  --------  --------------------
    3279f59f-c59d-46b5-824c-0d52f1c72538  GET       /candlepin/cons/UUID
    ab2a5a6c-d2f4-4557-a4f4-60ed760ddd61  GET       /candlepin/cons/UUID

    No processing request is open in the end of file.
    
