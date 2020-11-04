import os
import urllib.request
import logging
from pprint import pprint
from vkapi import VkApi

import config

def getPhotoUrls(photos):
    photoUrls = []
    for photoItem in photos:
        maxAvailSize = max([int(x.split('_')[1]) for x in photoItem.keys() if x.startswith("photo_")])
        photoUrls.append(photoItem['photo_' + str(maxAvailSize)])
    return photoUrls

def downloadPhotos(outDir, urls):
    if not os.path.exists(outDir):
        os.makedirs(outDir)
        
    for photoUrl in urls:
        file = '%s/%s' % (outDir, photoUrl.rsplit('/', 1)[-1])
        if not os.path.exists(file):
            print('        ',  photoUrl)
            urllib.request.urlretrieve(photoUrl, file)


#logging.basicConfig(level=logging.DEBUG)

api = VkApi(config.ACCESS_TOKEN)
users = api.getUsersByUids(config.UIDS)
for user in users:
    userId = user['id']
    userName = '%s %s' % (user['first_name'], user['last_name'])
    albums = api.getUserAlbums(userId)

    print('%s (%d) - %d albums' % (userName, userId, len(albums)))

    for album in albums:
        outDir = '%s/%s (%d)/%s' % (config.OUT, userName, userId, album['title'] + ' (' + str(album['id']) + ')')

        print('    "%s" - %d photos' % (album['title'], album['size']))

        photoUrls = getPhotoUrls(api.getPhotosFromAlbum(album))
        downloadPhotos(outDir, photoUrls)



