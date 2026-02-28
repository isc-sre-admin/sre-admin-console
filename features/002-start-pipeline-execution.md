# Start Pipeline Execution 

The end user will need a screen or a dialog to start the execution of a pipeline.
This will be the same screen for each pipeline, but it will need to have a different
form with different input text fields, to match the inputs in the contract. 

The input text fields will need to allow for both required and optional inputs, 
and will need to provide reasonable warning messages if an input is missing when
the submit button is clicked. 

The end user will need to select a research group / enclave from a dropdown (probably 
with typeahead as the number of enclaves grows) as one of the inputs. This will
provide the identifier for the backend's destation_account_id input. 

Once the execution of a pipeline is started, the end user may want to click through
to see the details of the execution (see 003-pipeline-execution-screen) or they may want 
to stay on the landing page and take another action while they wait for the pipeline
to execute. 


