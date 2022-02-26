# import io
# import os.path
import pickle
# from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

""" original resouce:
https://qiita.com/akabei/items/f25e4f79dd7c2f754f0e
"""

def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = Credentials.from_service_account_file('autotrade-ml-37ca46be841d.json')

    service = build('drive', 'v3', credentials=creds)

    # # Call the Drive v3 API
    # results = service.files().list(
    #     pageSize=10, fields="nextPageToken, files(id, name)").execute()
    # items = results.get('files', [])
    #
    # if not items:
    #     print('No files found.')
    # else:
    #     print('Files:')
    #     for item in items:
    #         print(u'{0} ({1})'.format(item['name'], item['id']))
    file = service.files().get(fileId='1lVZNFTmTDCQK-eG19OE5bYRcN3Fg4X8H').execute()
    print(file.get('name'))
    model = pickle.loads(service.files().get_media(fileId='1lVZNFTmTDCQK-eG19OE5bYRcN3Fg4X8H').execute())
    print(type(model))
    # model

    # fh = io.FileIO(file['name'], mode='wb')
    # downloader = MediaIoBaseDownload(fh, service.files().get(fileId='1MgacznIRKOcNleZMr1FRIwDcARkYjryf'))
    # done = False
    # while not done:
    #     _, done = downloader.next_chunk()

if __name__ == '__main__':
    main()
