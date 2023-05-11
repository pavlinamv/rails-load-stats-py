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
    

## Usage: 
    rails-load-stats <FILE> [SORTING_TYPE] [--without_stats]
    candlepin-load-stats <FILE> [SORTING_TYPE] [--without_stats]

        Possible sorting types are:
            1 or 'name': sort by the request_type
            2 or 'count': sort by the count
            3 or 'min': sort by the min time
            4 or 'max': sort by the max time
            5 or 'avg': sort by the avg time
            6 or 'mean': sort by the mean time
            7 or 8 or 'percentage': sort by the sum time / percentage


Example of usage:
   
![Screenshot_2023-05-10_06-211](https://github.com/pavlinamv/rails-load-stats-py/assets/22654167/f0f85965-def7-4ff9-9115-ce4ea6d85f63)

Now we can see the list of identificators + times spent on the request for any type of request. Request `PuppetcaController#index` (1st line in the previous table) is in `data_1.txt`, `HostsController#index` (2nd line) is in `data_2.txt`, ... 

![Screenshot_2023-05-11_07-17-15](https://github.com/pavlinamv/rails-load-stats-py/assets/22654167/7d0b9bee-1e2b-4267-8fc5-0fc7000287d3)
.
Corresponding `.png` file for `PuppetcaController#index` is in `plot_2.png`. In the file times spent on the request is depicted according to time order of the requests.

![Screenshot_2023-05-10_06-37-56](https://github.com/pavlinamv/rails-load-stats-py/assets/22654167/d0d3dcb8-f268-4523-8fad-a586f33acbc1)

![plot_001](https://github.com/pavlinamv/rails-load-stats-py/assets/22654167/05484dae-1d45-48f5-b500-0f3c0b8dba89)


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
    
