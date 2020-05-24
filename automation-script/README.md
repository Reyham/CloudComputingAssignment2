
1. Roles -> openstack-dependencies -> tasks -> main.yaml
	
	in the task - “ Upload python requirements file”,
	change the path to the requirements.txt file (present in the same directory.) in the “src” field accordingly.

2. Playbook.yaml

	Please provide the correct path to “hemanth_test.pem” file in the following places:
		vars -> ansible_ssh_private_key_file
	
	Note:

	1. Make sure to use the role: openstack-mount-volumes” only when creating the instances for the first time, or when re-creating the 	             Instances. Make sure to comment out this role in all other cases.
	
	2. In the play “Instance setup”, please perform the following operations:

		“”IF YOU HAVE ACCESS TO PRIVATE GIT-REPOSITORY””
	
		- Delete the secrets.yaml file in the automation-script directory
		- open a terminal window
		- change into the directory of playbook.yaml
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
  
3. Permissions for ssh key

		- run the following command in the terminal inside the automation-script directory:

			chmod +x hemanth_test.pem

4.	Run the automation script:
		
	Requirements:
		- openstack api password
		- opener.sh file
		- ssh key (hemanth_test.pem)
		- secrets.yaml file

	Steps to run:
		- change to the automation-script directory
		- Run the following command:
			./run-nectar.sh
		- enter your openstack api password
		- enter your administrator/root password
		- enter your ansible vault pasword.
