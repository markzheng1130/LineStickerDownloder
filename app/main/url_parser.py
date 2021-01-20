import asyncio
import threading
import time
import zipfile
from io import BytesIO

import aiohttp
import requests
from flask import current_app


# https://store.line.me/stickershop/product/12999
class StickerParser():
    sticker_type_to_url_map = {
        'static': 'android/sticker.png',
        'animated': 'iPhone/sticker_animation@2x.png',
        'popup': 'android/sticker_popup.png'
    }

    def __init__(self):
        self.sticker_title = None
        self.sticker_type = None
        self.sticker_url_list = []
        self.emoji_id = None
        self.emoji_count = 0
        self.sticker_file_list = []
        self.zip_file = None
        self.zip_file_name = None

    def parse(self, web_store_url: str):
        # Get html
        try:
            current_app.logger.info(f'[Get web store url][{web_store_url}]')
            web_store_html = requests.get(web_store_url)

        except Exception as e:
            raise e

        # Get lines
        lines = []
        for line in web_store_html.iter_lines():
            s = self._decode_html(line.decode('utf-8').strip())

            # Get sticker info
            if not self.sticker_title:
                self.sticker_title = self._get_sticker_title(s)
            if not self.sticker_type:
                self.sticker_type = self._get_sticker_type(s)
            if not self.emoji_id:
                self.emoji_id = self._get_emoji_id(s)
            if s.find('https://stickershop.line-scdn.net/sticonshop/v1/sticon/') > 0:
                self.emoji_count += 1
            lines += s.split(';')
        lines = [x for x in lines if x]

        # Print sticker info
        if self.sticker_title and self.sticker_type:
            current_app.logger.info(f'[Get title][{self.sticker_title}]')
            current_app.logger.info(f'[Get type][{self.sticker_type}]')
            if self.sticker_type == 'emoji':
                self.emoji_count //= 2  # html has duplicated emoji URL links.
                current_app.logger.info(f'[Get emoji id][{self.emoji_id}]')
        else:
            raise Exception(f'Cannot get sticker info, title: {self.sticker_title}, type: {self.sticker_type}')

        # Get sticker url list
        sticker_url_set = set()
        if self.sticker_type == 'emoji':
            sticker_url_set = self._parse_emoji_url()
        else:
            for line in lines:
                sticker_url = self._parse_sticker_url(line, self.sticker_type_to_url_map[self.sticker_type])
                if sticker_url:
                    sticker_url_set.add(sticker_url)

        if sticker_url_set:
            self.sticker_url_list = list(sticker_url_set)
            current_app.logger.info(f'[Get sticker count][{len( self.sticker_url_list)}]')

    def _get_sticker_title(self, s: str):
        target_l = 'data-share-text=\"'
        target_r = ' – LINE'
        l = s.find(target_l)
        r = s.find(target_r)
        if l == -1:
            return None
        else:
            return s[l + len(target_l): r]
    
    def _get_sticker_type(self, s: str):
        if s.find('canonical') != -1 and s.find('emojishop') != -1:
            return 'emoji'

        elif s.find('static&quot') != -1:
            return 'static'

        elif s.find('animation&quot') != -1:
            return 'animated'

        elif s.find('animation_sound&quot') != -1:
            return 'animated'

        elif s.find('popup&quot') != -1:
            return 'popup'  # Full screen

        elif s.find('popup_sound&quot') != -1:
            return 'popup'  # Full screen with sound

        else:
            return None

    def _get_emoji_id(self, s: str):
        target_l = 'var eventValue = \"'
        target_r = '\";'
        l = s.find(target_l)
        r = s.find(target_r)
        if l == -1:
            return None
        else:
            return s[l + len(target_l): r]

    def _decode_html(self, s: str):
        ascii_dict = {
            '&#39;': '\'',
            '&amp;': '&'
        }
    
        for key, value in ascii_dict.items():
            s = s.replace(key, value)
    
        return s

    def _parse_sticker_url(self, s: str, target: str):
        l = s.find('https')
        r = s.find(target)
        if l != -1 and r != -1:
            return s[l:r + len(target)]
        else:
            return None

    def _parse_emoji_url(self):
        emoji_url_set = set()
        for i in range(1, self.emoji_count + 1):
            emoji_url_set.add(f'https://stickershop.line-scdn.net/sticonshop/v1/sticon/{self.emoji_id}/iPhone/{i:03}.png')
        return emoji_url_set

    def download(self):
        start_time = time.time()
        asyncio.run(self._download_async())
        end_time = time.time()
        current_app.logger.info(f'[Time elapsed][{end_time - start_time}]')

    async def _download_async(self):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            await asyncio.gather(*[self._download_one(session, sticker_url, file_id) for file_id, sticker_url in enumerate(self.sticker_url_list)])

    async def _download_one(self, session, sticker_url, file_id):
        async with session.get(sticker_url) as response:
            self.sticker_file_list.append((f'{file_id}.png', await response.read()))  # (file_name, file_content)

    def _fix_weird_characters(self, s: str):
        fixed_s = s.replace('\\', '') \
            .replace(':', '') \
            .replace('*', '') \
            .replace('?', '') \
            .replace('\'', '') \
            .replace('>', '') \
            .replace('<', '') \
            .replace('|', '') \
            .replace(' ', '_') \
            .replace('　', '_') \
            .replace('é', 'e') \
            .replace('\'', '_') \
            .replace('`', '_') \
            .strip()

        return fixed_s

    def generate_zip_file(self):
        try:
            in_memory_zip = BytesIO()
            with zipfile.ZipFile(in_memory_zip, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
                for sticker_file in self.sticker_file_list:
                    zf.writestr(sticker_file[0], sticker_file[1])

            in_memory_zip.seek(0)
            self.zip_file = in_memory_zip
            self.zip_file_name = f'{self._fix_weird_characters(self.sticker_title)}.zip'

        except Exception as e:
            current_app.logger.info(f'[Compression exception][{e}]')
            raise e
