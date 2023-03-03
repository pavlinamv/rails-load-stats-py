rails-load-stats-py is [rails-load-stats script](https://github.com/pmoravec/rails-load-stats) writen in Python. Similarly as [rails-load-stats script](https://github.com/pmoravec/rails-load-stats) it processes a logfile of a Ruby on Rails app to analyze where the load to the app comes from. rails-load-stats-py is faster (especially for larger logfiles) than the original bash version and it contains some new features:
- list of particular requests from the most busy time (processed with the most concurrency)
- show progress bar during the input file processing
- create the plot with the numbers of open processing requests over the time (load of the RoR app over the time)

Similarly as [rails-load-stats script](https://github.com/pmoravec/rails-load-stats) it produces statistics about:
- Particular requests: how many requests against each method were raised, how much (min/max/avg/sum) time these took, and what percentage of overall execution time was spent by processing the different types of requests.
- Maximal level of concurrency: the peak number of requests that were processed in parallel.

Example output:

    there were 58960 requests taking 5187479 ms (i.e. 1.4 hours, i.e. 0.06 days) in summary
    
    type                                                      count      min    max      avg     mean     sum     percentage
    ------------------------------------------------------------------------------------------------------------------------
    MachineTelemetriesController#forward_request              948        37     20350    2271    284      2153808    41.52%
    CandlepinProxiesController#get                            25743      20     10322    34      26       879667     16.96%
    CandlepinProxiesController#serials                        11348      28     8643     50      35       576124     11.11%
    HostsController#facts                                     734        380    2043     617     591      453464      8.74%
    CandlepinProxiesController#server_status                  11375      18     4912     27      21       309910      5.97%
    ... 
    ...
    PuppetcaController#expiry                                 1          11     11       11      11       11          0.00%
    OrganizationsController#select                            1          5      5        5       5        5           0.00%
    
    
    Maximally 14 concurrent requsts when processing:
    Number     Time                    Request ID     Endpoint
    -------------------------------------------------------------------------------------------------------
    1          2023-01-10T05:47:40     9f6f862e       CandlepinProxiesController#get
    2          2023-01-10T05:47:40     7a94dbb1       CandlepinProxiesController#get
    ...
    ...
    14         2023-01-10T05:47:50     25dd72b2       CandlepinProxiesController#serials
    
    No processing requests are open in the end of file.


## Usage: 
    rails-load-stats-py <LOG_FILE> [SORTING_TYPE] [--with_plots] [--no_progress_bar]
          Possible sorting types are:
            1: sort by the name
            2: sort by the count
            3: sort by the min time
            4: sort by the max time
            5: sort by the avg time
            6: sort by the mean time
            7: sort by the sum time / percentage
          --with_plots 
          	- create a file 'plot.png' containing the number of open 
            	processing requests during the time. It is necessary to install
            	Python library mathplotlib for the option.


## Requirements:
Python version >= 3.6

for creating plots (--with_plots option):
mathplotlib

