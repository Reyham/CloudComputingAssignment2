#!/bin/bash

. ./openrc.sh; ansible-playbook -v --ask-become-pass playbook.yaml