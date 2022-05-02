#!/bin/bash
cd $HOME
read -p "Enter name of application: " appname
echo "Application: " $appname
echo "########## CREATING FOLDER ##########"
mkdir $appname
echo

read -p "Enter number of applications: " number
echo

for i in $(seq 1 $number)
do
  for yaml in modelos/*
  do
    echo "--> STARTING..."
    echo "--> COPYING YAML FILE..."
	
    filename=$(basename $yaml)
    cp $yaml $HOME/$appname/$filename
    file=$HOME/$appname/$filename
    echo "--> CHANGING FILE NAME..."
	
    newfile="$(echo ${file} | sed -e "s/-/$i-/")"
    mv "${file}" "${newfile}"
    echo "--> CHANGING YAML FILE CONTENT..."
	
    filefullname=$(basename "$newfile" .yaml)
    myarray=(`echo $filefullname | tr '-' ' '`)
    componentname=${myarray[0]}
    sed -i "s/#name/$componentname/g" $newfile
    if [[ $newfile == *"deployment"* ]]; then
      sed -i "s/#ID/$i/g" $newfile
    fi
    echo "--> "$componentname" FILE SUCCESSFULLY CREATED !"
    echo
	
  done
  echo "########## APPLICATION" $i "FILES CREATED ##########"
  echo
  
done
