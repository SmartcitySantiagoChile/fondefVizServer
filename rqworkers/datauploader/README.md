## dataUploader
Python script to upload files to Elasticsearch

To run the uploader, first download the files in the repo https://github.com/SmartcitySantiagoChile/elasticsearchInstaller/ and follow the instructions provided in the Readme.

After elasticsearch and cerebro are running, go to the dataUploader folder and execute:

    chmod +x requirements.sh
    ./requirements.sh
    
To load a file, the usage is:

    python3 loadData.py path/to/file

##### Arguments:

    file: path to the file that contains the data to load.
    
##### Optional:

    --host: the IP where ES is running. Default:"127.0.0.1".
    --port: the port that application is listening on. Default: 9200.
    --index: name of the index to create/use. If an index with the same name does not exist, the application will create it. Otherwise, it will use the existing index. By default, the name of the index is the extension of the file being uploaded.
    --chunk: number of docs to send to ES in one chunk. Default: 5000.
    --threads: number of threads to use. Default: 4.
    --timeout: timeout parameter of the ES client. Default:30 (in seconds.)

The default chunk size and number of threads are the ones that gave the best results when experimenting with different files, so using the defaults is recommended. Nevertheless, sometimes loading a big file can cause a timeout error; in this case, raising the timeout value should solve the issue (https://github.com/elastic/elasticsearch-py/issues/231)


##### About the mappings:
	
The mappings must be in a folder called ```mappings``` in the same directory where ```loadData.py``` is. The script uses the datafile extension to know what mapping to use so, if the mapping is called ```ext-template.json```, then the file must have extension ```ext```. For the mappings, only JSON format is accepted.

As the ES team is planning to deprecate doctypes, the mappings used to load the file should all use the default doctype that is ```doc```. If a property is a ```date```, then expliciting the format is recommended since ES is not able to parse all date formats and it may cause an exception. E.g.: 

    {
        "mappings": {
            "doc": {
                "properties":
		        "id": {"type": "long"},
		        "dateTime": {"type": "date", "format" : "yyyy-MM-dd HH:mm:ss"},
	                "type": {"type": "text"},
                    "description": {"type": "text"}
                }
            }
        }
    }

Additionally, is a property is listed as boolean only ```true``` and ```false``` values are accepted, using 0 and 1 will cause a ```MapperParsingException```. In some cases when the data is not properly parsed the option ```ignore malformed``` can be used (https://www.elastic.co/guide/en/elasticsearch/reference/current/ignore-malformed.html, check ```stop-template.json```.) 

##### About the extensions:

The extensions that this script loads are: ```expedition```, ```general```, ```od```, ```profile```, ```shape```, ```speed```, ```stop``` and ```travel```.

In order to load a file that has a different extension its mapping must be included in the mappings folder and its header must be added to ```datafile.py```. If not every column of the file is going to be loaded, if more columns need to be added or if its a nested file (meaning it has more than a line per document, like ```shape```), then a Python file that inherits from ```datafile.py``` must be created and the ```getHeader``` and ```makeDocs``` methods must be overwritten.
  
