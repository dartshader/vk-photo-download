# vk-photo-download
Python script for dumping vk user's albums


Script has been created for personal purposes, but may someone find this helpful

### Usage
Just fill corresponding fields in *config.py* file and then run `downloadAlbums.py` using python3
#### Configuration
* *OUT*:
The script will dump albums to the folder specified by this path
* *ACCESS_TOKEN*:
The vk API access token string that can be retrieved using a service such as https://vkhost.github.io/. Example: `e3b00314ac44298fc852b855b17077128418c149afbf46fb92427afbe84e41e4649b934ca495991b7c899`
* *UIDS*:
The list of vk ids to dump albums from. Example: `id12345678`
