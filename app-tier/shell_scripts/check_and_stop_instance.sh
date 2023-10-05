#!/bin/bash

emptyQueueCounter=$(cat /home/ubuntu/app-tier/emptyQueueCounter.txt)

if [ -z "$emptyQueueCounter" ] || ! [[ "$emptyQueueCounter" =~ ^[0-9]+$ ]]; then
    echo "emptyQueueCounter is not a valid number or is empty."
    exit 1
fi

if [ $emptyQueueCounter -ge 3 ]; then

    echo "Stopping the EC2 instance"
    
    instanceId=$(ec2metadata --instance-id)
    /home/ubuntu/.local/bin/aws ec2 stop-instances --instance-ids $instanceId --region us-east-1

    echo "" > /home/ubuntu/app-tier/emptyQueueCounter.txt
fi
