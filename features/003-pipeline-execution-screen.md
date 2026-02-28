# Pipeline Execution Detail and Progress

The end user will need a way to observe the execution of the pipeline and be informed if it fails and what the root cause of that failure was. This will probably involve interacting with CloudWatch logs in a particular log group. These are some obvious items that will need to be added to ./proposed-changes/queries so that the web application
has an easy way to get the list of executions, the execution details, and the stdout, downloadContent, and stderr logs from the backend. 



