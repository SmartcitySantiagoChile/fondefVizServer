#!/bin/bash

######################################################################
############## DJANGO-WORKER SERVICE CONFIGURATION FILE ##############
######################################################################

# On termination kill all workers, then reset trap
trap 'kill -TERM $(jobs -p); trap - INT;' TERM

# Read config file and start workers
while IFS='|' read -r -a line || [[ -n "$line" ]]; do
  for (( i=0; i<"${line[0]}"; i++ )) do
    <PYTHON_EXECUTABLE> <DJANGO_MANAGE_PY> rqworker ${line[1]} --worker-class "rqworkers.${line[2]}" &
    done
done < <PATH_TO_WORKER_CONFIG_FILE>
# First wait keeps the process running, waiting the workers to end
wait
# Second wait keeps the process running while the workers end gracefully
wait