#!/bin/bash

. ./1openrc.sh; ansible-playbook -v -i hosts.ini --ask-become-pass setup.yaml