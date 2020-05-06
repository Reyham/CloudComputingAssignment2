#!/bin/bash

. ./openrc.sh; ansible-playbook -i hosts.ini --ask-become-pass setup.yaml