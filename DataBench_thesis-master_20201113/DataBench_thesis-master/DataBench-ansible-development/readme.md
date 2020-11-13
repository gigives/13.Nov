# DataBench project Code

This is the repository where the DataBench project code is stored


## Folder structure

|    Folder name    |                                                     Description                                                    |
|:-----------------:|:------------------------------------------------------------------------------------------------------------------:|
| /AnsiblePlaybooks | Path to store all the ansible related files (playbooks, inventory, variables ...)                                  |
| /AnsiblePlaybooks/\<benchName>_specific | Path to store blocks of logic for each specific benchmark |
| /AnsiblePlaybooks/\<benchName>_specific/templates | Path to store jinja2 templates for the configuration files neede by the benchmark |
| /resultsProcessing| Path of the script to upload results to kafka. Also where the java code to parse the results is stored             |
| /vars             | Path where the benchmark-specific variable files are stored                                                                    |
| /benchmarks       | Path to store the binaries of the selected benchmarks                                                              |

## Requirements
- Ansible version > 2.0 installed in the host that will be used to run the benchmarks:
    - [Ansible-installation](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)
- Maven in the host to run the benchmarks (mainly to compile them but some of them need maven to run e.g: YCSB)
- Packages needed from ansible galaxy:
	- **yahoo benchmark:**
	   - ansible-galaxy install yashible.lein -> Lein is needed by the benchmark to generate events
## Configuration

## How to RUN

Before running any of the benchmarks we need to set up the *variables.yml* file.
We also need to fill the information in the *variables_{benchmark}.yml* specific to the desired benchmark that are in the *vars* folder.

It needs to be configured with the correct system information (hadoop lib folder, spark lib folder, hdfs address...)

After that we need to set the desired switches to true or false depending on what parts of the benchmarks we want to run.

We have playbooks to run each of the benchmarks independently, the commands to run each of them are as follow:

* [yahoo-streaming-benchmark](https://github.com/yahoo/streaming-benchmarks):
```
ansible-playbook -i variables.yml Benchmark_yahooBenchmark.yml -v
```
* [HiBench](https://github.com/intel-hadoop/HiBench):
```
ansible-playbook -i variables.yml Benchmark_HiBench.yml -v
```
* [TPCx-BB](http://www.tpc.org/tpcx-bb/default.asp):
```
ansible-playbook -i variables.yml Benchmark_TPCx-BB.yml -v
```
* [YCSB](https://github.com/brianfrankcooper/YCSB):
```
ansible-playbook -i variables.yml Benchmark_YCSB.yml -v
```
* [SparkBench](https://github.com/CODAIT/spark-bench):
```
ansible-playbook -i variables.yml Benchmark_SparkBench.yml -v
```

## Guidelines on creating new playbooks

The integrated benchmarks are designed to be run on target hosts where internet connection is not fully available. To overcome this constraint we have created the playbooks splitted in 2 parts, a part executed locally and the actual run of the benchmark executed in the target host.

The structure of a playbook is the following:

Local:

	- Check that the results path exists

Target host:
	
	- Load variables files
	- Get the benchmark code (from github, scp...)
	- Ensures the path to store the results exists
	- Configure the benchmark
	- Run the benchmark
	- Copy the results back to local

Local:

	- Send the results to kafka


### Reusable playbooks
There are some playbooks created to help developing new playbooks to integrate benchmarks into the toolbox.

One of them is the playbook in charge of sending the results of the benchmark to kafka:

	ansiblePlaybooks/Results_SendToKafka.yml

This playbook requires as input the following arguments:

* **kafka_broker**: Url and port to the kafka broker
* **topicName**: Name of the topic to send the results to. Must end with _results
* **benchName**: Name of the benchmark that creates the results
* **local_resultsPath**: Path where the results are stored

To use this playbook in a new playbook we can just add the following block:

	- block:
      - include: Results_SendToKafka.yml kafka_broker=130.206.113.246:9092 topicName=YCSB_results benchName=YCSB local_resultsPath=../results/YCSB/results
    when: autoSendResults