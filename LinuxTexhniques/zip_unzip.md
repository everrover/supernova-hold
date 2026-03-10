

```sh
sudo apt install zip

# zip
zip myfiles.zip file1.txt file2.txt file3.txt
zip -r archive.zip directory_name/
zip -r archive.zip directory_name/ -x "*.log"
zip -e archive.zip file1.txt
# unzip
unzip archive.zip -d <PATH>

## .tar.gz compress
tar -czvf archive_name.tar.gz files1 files2 files3 folder/
tar -xzvf archive_name.tar.gz -C <PATH>


```