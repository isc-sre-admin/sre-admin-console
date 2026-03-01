# Pipeline Execution Detail and Progress

The end user will need a way to observe the execution of the pipeline in detail and be informed if it fails and what the root cause of that failure was. 

Each execution pipeline label should be a link. Clicking on it should take the end user to a 
pipeline execution detail screen that provides a high-level view of the steps in the pipeline
and show them which step is currently executing. It should update dynamically as the execution
progresses. Clicking on any given step should provide a list of the input and outputs for 
that step. If a step fails, it should be marked in red and clicking on it should show the 
root cause of the failure. 

This will probably involve interacting with CloudWatch logs in a particular log group using queries. There are some obvious items that will need to be added to ./proposed-changes/queries so that the web application has an easy way to get the list of executions, the execution details, and the stdout, downloadContent, and stderr logs from the backend. 





