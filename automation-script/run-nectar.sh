#!/bin/bash

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

. ./unimelb-comp90024-2020-grp-48-openrc.sh; ansible-playbook --ask-become-pass playbook.yaml