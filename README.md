rails-load-stats.py and candlepin-load-stats.py scripts for creating statistics. Both scripts work quite similarly.

## rails-load-stats.py

rails-load-stats.py is [rails-load-stats script](https://github.com/pmoravec/rails-load-stats) writen in Python. Similarly as [rails-load-stats script](https://github.com/pmoravec/rails-load-stats) it processes a logfile of a Ruby on Rails app to analyze where the load to the app comes from.  Similarly as [rails-load-stats script](https://github.com/pmoravec/rails-load-stats) it produces statistics about:
- Particular requests: how many requests against each method were raised, how much (min/max/avg/sum) time these took, and what percentage of overall execution time was spent by processing the different types of requests.
- Maximal level of concurrency: the peak number of requests that were processed in parallel.

rails-load-stats-py is faster than the original bash version (especially for larger logfiles) and it contains some new features:
- list of particular requests from the most busy time (processed with the most concurrency)
- if "--without_stats" option is not used, it creates directory "`stats` + name of the input file" and for each request type it creates two files in the directory:
    - plot with the times of all requests of the type (sorted by the timestamp of the request)
    - text file containing the time of the request and its unique id (sorted by the size of time spent on the request)

Example output:
  
    there were 58960 requests taking 5187479 ms (i.e. 1.44 hours, i.e. 0.06 days) in summary

    
        request_type                                        count    min    max    avg    mean      sum    percentage
    --  ------------------------------------------------  -------  -----  -----  -----  ------  -------  ------------           
    1  MachineTelemetriesController#forward_request          948     37  20350   2271     280  2153800         41.12
    2  CandlepinProxiesController#get                      25743     20  10322     34      23   879667         16.36
    3  CandlepinProxiesController#serials                  11348     28   8643     50      35   576124         11.11
    4  HostsController#facts                                 734    580   2043    617     590   453464          8.74
    5  CandlepinProxiesController#server_status            11375     18   4612     27      21   309910          5.97

    ... 
    ...
    15  SmartProxiesController#pulp_storage                     1    149    149    149     149      149          0
    16  SmartProxiesController#pulp_status                      1    215    215    215     215      215          0

    
    
    Maximally 14 concurrent requests when processing:
      Number  Time                 Request ID    Endpoint
    --------  -------------------  ------------  ----------------------------------------
       0  2023-01-10T05:47:40  9f6f862e      CandlepinProxiesController#get
       1  2023-01-10T05:47:40  7a94dbb1      CandlepinProxiesController#get
    ...
    ...
       6  2023-01-10T05:47:41  793acd43      CandlepinProxiesController#get
    
    No processing requests are open in the end of file.


## Usage: 
    rails-load-stats <FILE> [SORTING_TYPE] [--without_stats]
    candlepin-load-stats <FILE> [SORTING_TYPE] [--without_stats]

        Possible sorting types are:
            1 or 'name': sort by the action and request_type
            2 or 'count': sort by the count
            3 or 'min': sort by the min time
            4 or 'max': sort by the max time
            5 or 'avg': sort by the avg time
            6 or 'mean': sort by the mean time
            7 or 8 or 'percentage': sort by the sum time / percentage


Example of usage:
   
![Screenshot_2023-05-08_19-57-29](https://user-images.githubusercontent.com/22654167/236896304-3f19f555-a471-46f1-8d8b-61448dd102a7.png)
    
Now we can see the list of identificators + times spent on the request for any type of request. Request `Test_Brno` (1st line in the previous table) is in `data_1.txt`, `Test_Olomouc` (2nd line) is in `data_2.txt`, ...
    
![Screenshot_2023-05-08_20-01-51](https://user-images.githubusercontent.com/22654167/236897250-fda8420e-e79d-4544-9344-8dc6305450b6.png)

Corresponding `.png` file for Test_Olomouc is in `plot_2.png`

    [localhost]$ gimp stats_test.log/plot_2.png

![plot_2](https://user-images.githubusercontent.com/22654167/236889579-cd4d5df6-63eb-4a60-954f-686c41536ced.jpg)


## Requirements:
Python version >= 3.6

tabulate - library for printing tables

mathplotlib - library for creating plots (if --without_stats is not used)


## candlepin-load-stats.py

candlepin-load-stats.py is similar as rails-load-stats.py script. It processes a candlepin logfile to analyze where the load to the app comes from. It works the same as rails-load-stats.py, and have the same usage and requirements.

Example output:

    there were 149084 requests taking 2137814 ms (i.e. 0.59 hours, i.e. 0.02 days) in summary

    action: request_type                                         count    min    max    avg    mean     sum    percentage
    --  ---------------------------------------------------------  -------  -----  -----  -----  ------  ------  ------------
    1  GET  :/candlepin/consumers/UUID/certificates/serials         25856      5   1714     23      14  594799         27.82
    2  GET  :/candlepin/consumers/UUID                              16071      3    787     28      19  462696         21.64
    3  GET  :/candlepin/consumers/UUID/content_overrides            34666      3    376      9       6  316487         14.8
    4  GET  :/candlepin/consumers/UUID/accessible_content           16034      4    389     14       9  227700         10.65
    ...
    ...

    Maximally 2 concurrent requests when processing:
    id                                    action    request_type
    ------------------------------------  --------  -----------------
    3279f59f-c59d-46b5-824c-0d52f1c72538  GET       /candlepin/status
    ab2a5a6c-d2f4-4557-a4f4-60ed760ddd61  GET       /candlepin/status

    No processing request is open in the end of file.
    
