# Landing Page

The admin console will need a landing page that will act at the starting point
for end user workflows. 

The end user will be focused on these primary top-level workflows:
1. Setting up new enclaves 
2. Creating and configuring AWS resources inside existing enclaves
3. Installing software via Ansible (Linux) or Powershell (Windows) on running virtual desktops or virtual machines


# Setting up new enclaves
Enclaves are actually AWS accounts that are created through another out-of-band 
process, so the setup of a new enclave happens after the AWS account has been created
under and existing AWS Organization, and onboarded into Control Tower using the 
Landing Zone Accelerator framework. This onboarding process includes the creation 
of IAM roles, policies, permission sets, identity center assignments, VPC network 
setup, etc. 

So the first thing the end user needs to do in a new enclave is to run the 
provision-ad-connector pipeline. This creates an AD Connector in the destination account (aka enclave), configures MFA for it, registers it as a directory with Amazon Workspaces, 
sets up the right WorkSpaces branding, and creates a new Systems Manager Hybrid Activation
so that the WorkSpace can activate itself when its SSM agent first connects to Systems Manager. 

There are a number of different pipelines the end user can run, and it makes sense for 
the landing page to have one section that shows what pipelines are currently executing and allows them to switch to a tab in that section to see what pipelines have executed in the past (probably filtered to show the last 7 days, with the option to pick another relative range -- e.g. 30 or 60 days, and also to specific an absolute time frame by start and end dates). 

# Creating and configuring AWS resources inside existing enclaves

The first resources that generally need to be created in each enclave are Amazon WorkSpaces. These come in two flavors: Linux and Windows. The end user will need to be 
able to pick the appropriate existing WorkSpace in the source account and use its workspace_id as an input for kicking off one of two pipelines:
1. Provision Linux WorkSpace
2. Provision Windows WorkSpace

They will also need to pick the AD user to associate with that WorkSpace. This is another key input for the pipeline. As part of this process, they will need to pick which research group this AD user belongs to. There is a one-on-one association betweenr research groups and enclaves. 

Another very similar activity is kicking off ones of these pipelines to deploy other computational resources in the enclaves:
1. Provision EC2 instance
2. Provision AWS Batch Computational Environment (not implemented yet, planned for future)

These computational resources will need to be created to allow researchers to run analyses that 
require more computational power than is easily available on the WorkSpaces (or to avoid having
to provision a larger WorkSpace to run analyses that only run for a short period of time). 

# Installing software via Ansible (Linux) or Powershell (Windows) on running virtual desktops or virtual machines

This is a more complex activity for the end user, where they need to be able to develop a new 
Ansible playbook or Powershell script, or to modify a playbook or script that already exists. They will want to modify these files and then push them to a repository or S3 bucket where they can then
be transferred to the WorkSpace or EC2 instance by invoking the appropriate operation. 

The UI needs to give them the ability select files from a directory, edit those files, save them locally, and then commit them / push them out for deployment. 

