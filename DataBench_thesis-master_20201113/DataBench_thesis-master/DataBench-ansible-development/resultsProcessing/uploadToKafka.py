from confluent_kafka import Producer
# pip install confluent-kafka

import argparse
import glob, os, datetime


def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print('Message delivery failed: {}'.format(err))
        raise ValueError("Error: Message Not Delivered")
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(),
                                                    msg.partition()))


def sendMessage(topic, data, key, producer):
    """
    Method used to send data to the desired topic with the desired key
    """
    producer.poll(0)
    producer.produce(topic, data.encode('utf-8'), key, callback=delivery_report)
    producer.flush()


def yahooBench(args):
    """
    The yahoo streaming benchmark result are 2 files: updated.txt and seen.txt
    From their documentation:
    "The current set of results that we care about are comparing the latency
    that a particular processing system can produce at a given input load.
    The result of running a test creates a few files
    data/seen.txt and data/updated.txt
    data/seen.txt contains the counts of events for different campaigns and
    time windows.
    data/updated.txt is the latency in ms from when the last event was emitted
    to kafka for that particular campaign window and when it was written into Redis."

    We need to be able to send this to kafka in a way that we can, later on, identify the correct pair of messages that create the complete result for a single run.
    I think the best option for this is to concatenate the a timestamp to the user id as the key of the message and send both files with that same key.
    """

    # Create the kafka producer with the correct configuration
    p = Producer({'bootstrap.servers': args.bootstrap})

    files_path = os.path.join(args.folder, "*.txt")
    files = sorted(glob.iglob(files_path), key=os.path.getctime, reverse=True)
    if len(files) >= 2:

    	# We get the timestamp for the id from the filename
        filename_extended = files[0].split('/')
        filename = filename_extended[len(filename_extended) - 1].split('.')[0]
        fileTS = filename.split('_')[0]

        print(fileTS)

        # Send the seen.txt file
        with open(files[0], 'r') as myfile:
            data = myfile.read().replace('\n', '|')

        # print('File content: '+data)
        sendMessage(args.topic, data, args.id + "|" + filename, p)

        # We get the timestamp for the id from the filename
        filename_extended = files[1].split('/')
        filename = filename_extended[len(filename_extended) - 1].split('.')[0]
        fileTS = filename.split('_')[0]

        # Send the updated.txt file
        with open(files[1], 'r') as myfile:
            data = myfile.read().replace('\n', '|')

        # print('File content: '+data)
        sendMessage(args.topic, data, args.id + "|" + filename, p)
    else:
        print("No data in the folder to be sent")


def hiBench(args):
    """
    Results are written into the hibench.report file with the following CSV format:
    test_name end_date <jobstart_timestamp,jobend_timestamp> size_in_bytes duration_ms throughput
    Beware that the actual result file does not contain the column header  above.
    """
    p = Producer({'bootstrap.servers': args.bootstrap})
    ts = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    files_path = os.path.join(args.folder, "hibench*.report")
    files = sorted(glob.iglob(files_path), key=os.path.getctime, reverse=True)
    if len(files) >= 1:
        # Send the result file
        with open(files[0], 'r') as myfile:
            data = myfile.read()

        # print('File content: '+data)
        sendMessage(args.topic, data, args.id + "|" + ts, p)
    else:
        print("No files found in the specified directory: " + args.folder)

def ownperf(args):
    """
    Results are written in a single file
    """
    # Create the kafka producer with the correct configuration
    p = Producer({'bootstrap.servers': args.bootstrap})

    files_path = os.path.join(args.folder, "*Results.txt")

    print(files_path)
    files = sorted(glob.iglob(files_path), key=os.path.getctime, reverse=True)
    if len(files) >= 1:
        # We get the first file from the array, which is the newest one
        filename_extended = files[0].split('/')
        filename = filename_extended[len(filename_extended) - 1].split('.')[0]
        print(filename)
        with open(files[0], 'r') as myfile:
            data = myfile.read().replace('\n', '|')
        sendMessage(args.topic, data, args.id + "|" + filename, p)  
        print("ownperf")
    else:
        print("No files found in the specified directory: " + args.folder)




def bigbench(args):
    # Create the kafka producer with the correct configuration
    p = Producer({'bootstrap.servers': args.bootstrap})
    files_path = os.path.join(args.folder, "*.txt")

    print(files_path)
    files = sorted(glob.iglob(files_path), key=os.path.getctime, reverse=True)
    if len(files) >= 1:
        # We get the timestamp for the id from the filename
        filename_extended = files[0].split('/')
        filename = filename_extended[len(filename_extended) - 1].split('.')[0]
        fileTS = filename.split('_')[0]

        files_regexp = os.path.join(args.folder, fileTS+"*.txt")
        files_by_timestamp = sorted(glob.iglob(files_regexp), key=os.path.getctime, reverse=True)

        for file in files_by_timestamp:
            # We get the timestamp for the id from the filename
            filename_extended = file.split('/')
            filename = filename_extended[len(filename_extended) - 1].split('.')[0]
            print(filename)
            with open(file, 'r') as myfile:
                data = myfile.read().replace('\n', '|')
            sendMessage(args.topic, data, args.id + "|" + filename, p)
        print("YCSB")
    else:
        print("No files found in the specified directory: " + args.folder)



    print("BigBench")

def bigbenchv2(args):
    # Create the kafka producer with the correct configuration
    p = Producer({'bootstrap.servers': args.bootstrap})
    ts = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    files_path = os.path.join(args.folder, "times.csv")
    files = sorted(glob.iglob(files_path), key=os.path.getctime, reverse=True)
    if len(files) >= 1:
        # Send the result file
        with open(files[0], 'r') as myfile:
            data = myfile.read().replace('\n', '-')

        # print('File content: '+data)
        sendMessage(args.topic, data, args.id + "." + ts, p)
    else:
        print("No files found in the specified directory: " + args.folder)

def ycsb(args):
    """
    Results are written in two parts, one for the load of the data and another for the actual run of the benchmark.
    """
    # Create the kafka producer with the correct configuration
    p = Producer({'bootstrap.servers': args.bootstrap})

    files_path = os.path.join(args.folder, "*Results.txt")

    print(files_path)
    files = sorted(glob.iglob(files_path), key=os.path.getctime, reverse=True)
    if len(files) >= 1:
        # We get the timestamp for the id from the filename
        filename_extended = files[0].split('/')
        filename = filename_extended[len(filename_extended) - 1].split('.')[0]
        fileTS = filename.split('_')[0]

        files_regexp = os.path.join(args.folder, fileTS+"*.txt")
        files_by_timestamp = sorted(glob.iglob(files_regexp), key=os.path.getctime, reverse=True)

        for file in files_by_timestamp:
            # We get the timestamp for the id from the filename
            filename_extended = file.split('/')
            filename = filename_extended[len(filename_extended) - 1].split('.')[0]
            print(filename)
            with open(file, 'r') as myfile:
                data = myfile.read().replace('\n', '|')
            sendMessage(args.topic, data, args.id + "|" + filename, p)
        print("YCSB")
    else:
        print("No files found in the specified directory: " + args.folder)


def invalid(args):
    print("The benchmark name passed as argument is not supported, sending the most recent file from the results folder as default")
    """
    Results are written in a single file
    """
    # Create the kafka producer with the correct configuration
    p = Producer({'bootstrap.servers': args.bootstrap})

    files_path = os.path.join(args.folder, "*Results.txt")

    print(files_path)
    files = sorted(glob.iglob(files_path), key=os.path.getctime, reverse=True)
    if len(files) >= 1:
        # We get the first file from the array, which is the newest one
        filename_extended = files[0].split('/')
        filename = filename_extended[len(filename_extended) - 1].split('.')[0]
        print(filename)
        with open(files[0], 'r') as myfile:
            data = myfile.read().replace('\n', '|')
        sendMessage(args.topic, data, args.id + "|" + filename, p)
        print("Most recent results file sent to kafka")
    else:
        print("No files found in the specified directory: " + args.folder)

switcher = {
    "yahoobench": yahooBench,
    "hibench": hiBench,
    "BigBench": bigbench,
    "BigBenchV2": bigbenchv2,
    "YCSB": ycsb,
    "ownperf": ownperf
}


def decideBenchmark(argument, args):
    func = switcher.get(argument, invalid)
    return func(args)


def main():

    # Parse the arguments into variables
    parser = argparse.ArgumentParser(description='Write the content of the file to the kafka topic')
    parser.add_argument('-t', '--topic',
                        help='Name of the kafka topic', required=True)
    parser.add_argument('-f', '--folder',
                        help='Path to the folder where the results are stored', required=True)
    parser.add_argument('-i', '--id',
                        help='Identifier of the client sending the message', required=True)
    parser.add_argument('-b', '--bootstrap',
                        help="Name or host of kafka's bootstrap server", required=True)
    parser.add_argument('-bn', '--benchname',
                        help="Name of the benchmark that generated the results to be sent")

    args = parser.parse_args()

    decideBenchmark(args.benchname, args)


if __name__ == "__main__":
    main()
