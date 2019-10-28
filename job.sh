#!/bin/bash

# Build Docker Image from the Dockerfile
docker build -t automation .

# Get current Date/Time & Create Release Dirs
date=$(date '+%Y_%m_%d_%H%M')
mkdir "$date"
mkdir "$date"/combined
mkdir "$date"/separeted

# Start Postgresql Docker Container
docker-compose -f /var/lib/orb/automation.yaml up -d

# Pause to Make Sure Container is UP
sleep 4

# Run Python Script to Create export_tables and Dump it to CSV Files
python /var/lib/orb/db.py

# Stop and Delete Postgresql Docker Container
docker stop automation
docker rm automation

# Copy & Move CSV Files to Release Dirs 
cp input_data/companies.csv  "$date"/combined
cp input_data/branches.csv "$date"/combined

mv input_data/companies.csv  "$date"/separeted
mv input_data/branches.csv "$date"/separeted

# Tar & Zip Release Files 
tar -zcvf "$date"/separeted/orb_companies.tar.gz "$date"/separeted/companies.csv
tar -zcvf "$date"/separeted/orb_branches.tar.gz "$date"/separeted/branches.csv

zip "$date"/combined/orb_data.zip "$date"/combined/*.*

# Clean Processed Files
rm "$date"/combined/*.csv
rm "$date"/separeted/*.csv

rm input_data/orb_*2*.csv
