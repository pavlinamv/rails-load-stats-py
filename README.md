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
            1 or 'name': sort by the action and request_type
            2 or 'count': sort by the count
            3 or 'min': sort by the min time
            4 or 'max': sort by the max time
            5 or 'avg': sort by the avg time
            6 or 'mean': sort by the mean time
            7 or 8 or 'percentage': sort by the sum time / percentage


Example of usage:
   
![Screenshot_2023-05-08_20-06-01](https://user-images.githubusercontent.com/22654167/236898372-eef71a87-cd42-4cae-9915-22939ff6bceb.png)
    
Now we can see the list of identificators + times spent on the request for any type of request. Request `Test_Brno` (1st line in the previous table) is in `data_1.txt`, `Test_Olomouc` (2nd line) is in `data_2.txt`, ...
    
![Screenshot_2023-05-08_20-07-04](https://user-images.githubusercontent.com/22654167/236915868-70defac6-02ae-48eb-b203-be0ff5cf7d5e.png)
Corresponding `.png` file for Test_Olomouc is in `plot_2.png`

![Screenshot_2023-05-08_20-07-29](https://user-images.githubusercontent.com/22654167/236898574-23476373-e11a-45c3-88b6-34cb8033fb83.png)

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
    
