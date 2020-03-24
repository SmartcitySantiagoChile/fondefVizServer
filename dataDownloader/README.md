## dataDownloader
Python script to download files from Elasticsearch

To run the downloader, first download the files in the repo https://github.com/SmartcitySantiagoChile/elasticsearchInstaller/ and follow the instructions provided in the Readme.

After elasticsearch and cerebro are running, go to the dataDownloader folder and execute:

    chmod +x requirements.sh
    ./requirements.sh
    
To download data from index to file, the usage is:

    python3 downloadData.py path/to/file index

##### Arguments:

    query: query that retrieve data.
    index: name of the index to use.
    file: path to the file that contains downloaded data from elasticsearch.


##### Optional:

    --host: the IP where ES is running. Default:"127.0.0.1".
    --port: the port that application is listening on. Default: 9200.

The default chunk size is the ones that gave the best results when experimenting with different numbers, so using the defaults is recommended.


##### About the extensions:

The indexes that this script downloads are: ```odbyroute```, ```profile```, ```shape```, ```speed```, ```stop``` and ```trip```.

  
