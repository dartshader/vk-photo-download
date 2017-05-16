import urllib.request
import urllib.parse
import urllib.error
import json
import time
import logging

class VkApiException(Exception):
    pass

class VkApi:
    """ VkApi class. Provides some methods for accessing VK API. """
    
    TOO_MANY_REQ_PER_SECOND_ERR = 6
    API_URL    = "https://api.vk.com/method/"
    API_VER    = "5.52"

    def __init__(self, access_token = None):
        """ Constructor
        Args:
            access_token (str): OAuth access token. Will be used for calls if provided.
        Returns:
            VkApi instance.
        """
        self.access_token = access_token

    def call_api(self, method, params):
        """ Just calls VK API
        Args:
            method (str): VK API method, see: https://new.vk.com/dev/methods
            params (dict): Params for given method.
        Returns:
            Response as dict
        """
        
        TRIES = 3
        DELAY = 3

        params["v"] = self.API_VER
        if self.access_token is not None:
            params["access_token"] = self.access_token 

        request_url = self.API_URL + method
        request_data = urllib.parse.urlencode(params, True).encode("ascii")
        logging.debug("requestUrl = %s\nrequestData = %s" % (request_url, request_data.decode("utf-8")))
        
        for try_number in range(1, TRIES + 1):
            try:
                with urllib.request.urlopen(request_url, request_data) as conn:
                    response = json.loads(conn.read().decode("utf-8"))
                    logging.debug("response = %s" % response)
                    if "error" in response:
                        if response["error"]["error_code"] == self.TOO_MANY_REQ_PER_SECOND_ERR:
                            logging.info("Too many requests per second, %d sec cooldown." % DELAY)
                            time.sleep(DELAY)
                            continue
                        else:
                            raise VkApiException(response["error"]) 
                    break
            except urllib.error.URLError as e:
                raise e    

        return response["response"]

    def getUsersByUids(self, uids, fields = ['uid', 'first_name', 'last_name'], nameCase = 'nom'):
        """ Get users by uids
        Args:
            uids (list): List of usres ids
            fields (list): See VK API Docs
            nameCase (str): See VK API Docs
        Returns:
            List of user objects(See VK API Docs) as dict
        """
        MAX_PER_REQUEST = 1000
        users = []
        for offset in range(0, len(uids), MAX_PER_REQUEST):
            users += self.call_api('users.get', {
                'user_ids': ','.join(str(x) for x in uids[offset : offset + MAX_PER_REQUEST]),
                'fileds': ','.join(fields),
                'name_case': nameCase})
        return users

    def getUserAlbums(self, ownerId, needSystem = True, needCovers = False):
        """ Get Albums owned by user. For args see VK API Docs
        Args:
            ownerId (str, int)
            needSystem (bool)
            needCovers (bool)
        Returns:
            List of album objects(See VK API Docs) as dict
        """
        return self.call_api('photos.getAlbums', {
            'owner_id': ownerId,
            'need_system': int(needSystem),
            'need_covers': int(needCovers)
            })['items']

    def getPhotosFromAlbum(self, album):
        """ Get photos from VK album
        Args:
            album (dict): Album object (see VK API Docs).
                          Or just {'owner_Id': __ownerId__, 'id': __albumId__}
        Returns:
            List of photo objects (see VK API Docs) as dict
        """
        MAX_PER_REQUEST = 1000
        photos = []
        for offset in range(0, album['size'], MAX_PER_REQUEST):
            photos += self.call_api('photos.get', {
                'owner_id': album['owner_id'],
                'album_id': album['id'],
                'offset': offset,
                'count': MAX_PER_REQUEST
                })['items']
        return photos