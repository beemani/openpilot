# External Storage

## Initial Setup
Create the mount point:
```
sudo mkdir -p /data/media/1
```
Format storage device:
```
sudo mkfs.ext4 /dev/sdg1
```
Mount the storage device:
```
sudo mount /dev/sdg1 /data/media/1
```
Create realdata folder:
```
sudo mkdir /data/media/1/realdata
```
Set permissions:
```
sudo chown -R comma:comma /data/media/1/
```


## To Mount
Mount the storage device:
```
sudo mount /dev/sdg1 /data/media/1
```


## To Unmount
Unmount the storage device:
```
sudo umount /dev/sdg1
```
