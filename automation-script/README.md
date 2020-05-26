############################################################
# # Cluster and Cloud Computing (COMP90024) Assignment 2 # #
# # The University of Melbourne                          # #
# # Group Number: 48                                     # #
# # Authors:                                             # #
# # 1. Hemanth Pavan Kumar Challa - 1064637              # #
# # 2. Sai Varun Reddy Ankireddy  - 1152791              # #
# # 3. Abhisha Nirmalathas        - 913405               # # 
# # 4. Saharsha Karki             - 1042219              # #
# # 5. Reyham Noorjono            - 1018055              # #
############################################################

1. Roles -> openstack-dependencies -> tasks -> main.yaml
	
	In the task - “ Upload python requirements file”:
		- Change the path to the requirements.txt file (present in the same directory.) in the “src” field accordingly.
		- A relative-path is provided in the script. You only need to perform the above step if the path doesn't work.

2. Playbook.yaml

	Please provide the correct path to “final_key.pem” file in the following places:
		vars:
			-	ansible_ssh_private_key_file: <path-to-ssh-key>
	A relative path is provided in the script. So, this should be done in case of failure.
	
	Note:

	1. Make sure to use the role: "openstack-mount-volumes” only when creating the instances for the first time, or when re-creating the instances. Make sure to comment out this role in all other cases.
	
	2. In the play “Instance setup”, please perform the following operations:

								“”IF YOU HAVE ACCESS TO PRIVATE GIT-REPOSITORY””
	
		- Delete the secrets.yaml file in the automation-script directory.
		- Open a terminal window.
		- Change into the directory of playbook.yaml file.
		- Type in the following command in the terminal:

			$ ansible-vault create secrets.yaml

			 	- This will ask to create a new vault password if you don’t have one already. Please do so.

			$ ansible-vault edit secrets.yaml

				- Now, click “ i “ on the keyboard to enter into insert mode.
				- Type in the following lines with your Github login details.
					
					gituser: <your-github-username>
					gitpass: <your-github-password>

				- Now, perform the following steps:

					1. Click “ESC” key on the keyboard.
					2. Enter “:wq“ and press Enter.

	3. If the git repository is public, you don't have to make any changes.
  
3. Permissions for ssh key

		- Run the following command in the terminal inside the automation-script directory:

			$ chmod 600 final_key.pem

4.	Run the automation script:
		
	Requirements:
		- openstack api password
		- opener.sh file
		- ssh key (final_key.pem)
		- secrets.yaml file (Only if the repository is not public.)

	Steps To Run:

		- Open a terminal window

		- Change to the automation-script directory

		- If you have access to private git repository, please perform the following changes:

			1. roles -> clone-repository -> tasks -> main.yaml

				- Change the shell value to the following: 

						git clone https://{{ gituser | urlencode }}:{{ gitpass | urlencode }}@github.com/Reyham4/CloudComputingAssignment2.git

			2. playbook.yaml

				- Uncomment the following lines:

					   vars_files:
  					     - secrets.yaml 

			3. run-nectar.sh

				- Replace the contents of the file with the following:
					
					#!/bin/bash

					. ./unimelb-comp90024-2020-grp-48-openrc.sh; ansible-playbook --ask-become-pass playbook.yaml --ask-vault-pass

		- If the repository is public, you don't have to perform any changes.

		- Run the following command:
			$ ./run-nectar.sh
		- Enter your openstack api password

		- Enter your administrator/root password

		- Enter your ansible vault pasword. (If asked. This will only be asked if the git repository is not public)
