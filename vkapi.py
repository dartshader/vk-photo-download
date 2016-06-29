import urllib.request
import urllib.parse
import urllib.error
import json
import time
import logging

TOO_MANY_REQ_PER_SECOND_ERR = 6

class VkApiException(Exception):
    pass

class VkApi:
    def __init__(self, accessToken = None):
        self.accessToken = accessToken

    def callApi(self, method, params):
        API_URL = "https://api.vk.com/method/"
        API_VER = "5.52"
        TRIES   = 3
        DELAY   = 3

        params["v"] = API_VER
        if self.accessToken is not None:
            params["access_token"] = self.accessToken

        requestUrl = API_URL + method
        requestData = urllib.parse.urlencode(params, True).encode("ascii")
        logging.debug("requestUrl = %s\nrequestData = %s" % (requestUrl, requestData.decode("utf-8")))

        for tryN in range (1, TRIES + 1):
            try:
                with urllib.request.urlopen(requestUrl, requestData) as conn:
                    response = json.loads(conn.read().decode("utf-8"))
                    logging.debug("response = %s" % response)
                    if "error" in response:
                        if response["error"]["error_code"] == TOO_MANY_REQ_PER_SECOND_ERR:
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
        MAX_PER_REQUEST = 1000
        users = []
        for offset in range(0, len(uids), MAX_PER_REQUEST):
            users += self.callApi('users.get', {
                'user_ids': ','.join(str(x) for x in uids[offset : offset + MAX_PER_REQUEST]),
                'fileds': ','.join(fields),
                'name_case': nameCase})
        return users

    def getUserAlbums(self, ownerId, needSystem = True, needCovers = False):
        return self.callApi('photos.getAlbums', {
            'owner_id': ownerId,
            'need_system': int(needSystem),
            'need_covers': int(needCovers)
            })['items']

    def getPhotosFromAlbum(self, album):
        MAX_PER_REQUEST = 1000
        photos = []
        for offset in range(0, album['size'], MAX_PER_REQUEST):
            photos += self.callApi('photos.get', {
                'owner_id': album['owner_id'],
                'album_id': album['id'],
                'offset': offset,
                'count': MAX_PER_REQUEST
                })['items']
        return photos