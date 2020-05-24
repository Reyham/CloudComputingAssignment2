# CloudComputingAssignment2

A cloud based solution written in Python that exploits a multitude of VMs across the UniMelb Research Cloud for harvesting tweets through Twitter APIs.

Technologies:
- Python
- OpenStack https://www.openstack.org/
- Ansible https://docs.ansible.com/ansible/latest/index.html
- Docker https://www.docker.com/
- Twitter Harvester https://developer.twitter.com/en
- AURIN openApi https://aurin.org.au/aurin-apis/
- CouchDB https://couchdb.apache.org/
- MapBox: https://www.mapbox.com/
- D3.js: https://d3js.org/

On a linux system:
sudo apt-get update
sudo apt-get install


Install Python dependencies:
pip -r requirements.txt

To run the Twitter Harvester:
python3 run.py [stream | cloud | home] (any combination of 3)


Install NodeJS dependencies:
