######################################################################
#################### DJANGO-WORKER SERVICE README ####################
######################################################################

The django-worker service is made to keep workers (of django-rq)
running in the background instead of having shells for every worker
open. It's bound to the apache2 service, so it will start and stop
with it (note: apache2 will try to start it, but if it fails to load,
apache will work anyways).

This service is controlled by the djangoRqWorkers.sh script, which
reads the worker_config.txt file and runs the workers there specified.
Each row on this file has the following format:
<Num>|<Space-separated names>|<Python class name>

The previous <Python class name> is the Python path to the class that
the workers created will be from, specified relative to the rqworkers
folder, allowing for worker customization and pre-loading of Python
modules if necessary. The <Space-separated names> are the queues that
the worker will be listening to. They must be specified in the
settings of the project. Finally, the <Num> is the number of workers
to be called with the succeeding configuration.

################### A NOTE ON WORKER CUSTOMIZATION ###################

In the implementation of a custom worker the imported modules in the
class load at the time of the rqworker in the service script starts.
This can be useful for pre-loading functions if a worker class will be
working with them repeatedly, as it will have them in cache and not
reload them every time that worker has to execute the function.
However is important to have in mind that because of that if the code
of the function is changed while the worker is running, it won't be
updated for the worker unless a restart is done.