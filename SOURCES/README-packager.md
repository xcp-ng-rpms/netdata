# netdata

Netdata is the fastest way to visualize metrics. It is a resource efficient, highly optimized system for collecting and visualizing any type of realtime time-series data, from CPU usage, disk activity, SQL queries, API calls, web site visitors, etc.

netdata tries to visualize the truth of now, in its greatest detail, so that you can get insights of what is happening now and what just happened, on your systems and applications.

## Plugins

### Activate mysql plugin

Be sure to have python library for mysql MySQLdb (faster) or PyMySQL (slower)

* Fedora

    ````
    sudo dnf install python3-mysql
    ````
    
* Epel

    ````
    yum install MySQL-python
    ````

Create netdata mysql user

````
CREATE USER 'netdata'@'localhost';
GRANT USAGE on *.* to 'netdata'@'localhost';
FLUSH PRIVILEGES;
````
