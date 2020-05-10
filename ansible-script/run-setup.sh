#!/bin/bash

. ./openrc.sh; ansible-playbook -v -i hosts.ini --ask-become-pass setup.yaml