# netdata

Netdata is the fastest way to visualize metrics. It is a resource efficient, highly optimized system for collecting and visualizing any type of realtime time-series data, from CPU usage, disk activity, SQL queries, API calls, web site visitors, etc.

netdata tries to visualize the truth of now, in its greatest detail, so that you can get insights of what is happening now and what just happened, on your systems and applications.

## Building package

1. First of all, download the source tarball from github
2. Create tarball of go dependencies for the new netdata version to avoid the need of being connected during build time.
    
    ```
    ./create-go-vendor.sh <VERSION>
    ```
3. Build package as usual

## Modifying stock config file

Netdata have a stock of config files located now in /usr/lib/netdata/conf.d directory (previous path was /etc/netdata/conf.d). 

To overwrite this default config files, use the edit-config script in /usr/libexec/netdata directory.

Eg: Overriding /usr/lib/netdata/conf.d/python.d.conf

    sudo /usr/libexec/netdata/edit-config python.d.conf

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
