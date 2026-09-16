import requests
import asyncio
import aiohttp
import ssl

import logging

import telebot
from telebot import apihelper, asyncio_helper  
from aiohttp_socks import ProxyConnector
from telebot.types import InputMediaPhoto, InputMediaVideo 
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InputMediaPhoto, InputMediaVideo, InputMediaDocument, InputMediaAudio 

import db
from db import take_user_name, create_message_pair, create_database

create_database()
logging.basicConfig(
    level=logging.INFO,  # Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s',  # Формат строки лога
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),  # Запись в файл
        logging.StreamHandler()  # Вывод в консоль
    ]
)

PROXY_URL = 'socks5://127.0.0.1:10808'


BOT_TOKEN = ""
CHAT_ID = -1002594133059
MAX_BOT_TOKEN = ''

chat_id = -78563958726708
bot = AsyncTeleBot(BOT_TOKEN)


# url = f"https://platform-api2.max.ru/messages?chat_id={chat_id}"
url = f"https://platform-api2.max.ru/updates?types=message_created,message_edited,message_removed "
max_api_url = 'platform-api2.max.ru'

headers = {
    "Authorization": MAX_BOT_TOKEN
}
cert = 'Russian_Trusted_Root_CA.cer'





async def poll_api(bot):
    ssl_context = ssl.create_default_context()
    ssl_context.load_verify_locations(cafile=cert)
    backoff_delay = 1  # Начальная задержка при ошибке (в секундах)
    
    # Настраиваем клиентскую сессию с поддержкой долгого удержания соединения
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    async with aiohttp.ClientSession(connector=connector) as session:
      
        while True:
          
            
            try:
                async with session.get(url=url, headers=headers ) as response:
                 
                    if response.status != 200:
                        logging.error(f"Ошибка сервера: {response.status}. Повтор через {backoff_delay} сек.")
                        await asyncio.sleep(backoff_delay)
                        backoff_delay = min(backoff_delay * 2, 60) 
                        continue
                    
           
                    data = await response.json()
                    backoff_delay = 1


                    for update in data['updates']:
                        #print(str(data['updates'][i]) + "\n")
                        print(update)
                        print("\n")
                        if update.get('message') == None:
                            continue

                        if update['message']['body'].get('attachments') != None:
                                attachments = update['message']['body']['attachments']
                                text = update['message']['body']['text']
                                print(text)
                                photos = []
                                audios = []
                                files = []
                                videos = []
                               
                                
                                for u in attachments:
                                    if u.get('type') == 'image':
                                        photos.append(u['payload']['url'])


                                    if u.get('type') == 'video':
                                         vurl = f"https://{max_api_url}/videos/{u['payload']['token']}"
                                         vresponse = requests.get(url=vurl,  headers=headers, verify=cert)
                                         videos.append(vresponse.json())
                                         print(vresponse.json())

                                         
                                    if u.get('type') == 'audio':
                                        audios.append(u['payload']['url'])


                                    if u.get('type') == 'file':
                                        files.append(u['payload']['url'])


                                
                                if photos:
                                            if len(photos) <= 10:
                                                media = []
                                                name = take_user_name(update['message']['sender']['user_id'], 'MAX') 
                                                if  name == False: 
                                                    name = 'Неизвестный пользователь'
                                                for i, ph in enumerate(photos):
                                                    caption_text = name + "\n" + text if i == 0 else None
                                                    media.append(InputMediaPhoto(media=ph , caption=caption_text))
                                                tg_send_mes = await bot.send_media_group(chat_id=CHAT_ID, media=media)
                                                await create_message_pair(mMAX_id=update['message']['body']['mid'], mTG_id=tg_send_mes[0].message_id, name=name)
                                                logging.info(f"Сообщение PHOTO (без текста) tg: {tg_send_mes.message_id} MAX: {update['message']['body']['mid']} успешно отправлено!")

                                if videos:
                                            if len(videos) <= 10:
                                                media = []
                                                name = await take_user_name(update['message']['sender']['user_id'], 'MAX') 
                                                if  name == False: 
                                                    name = 'Неизвестный пользователь'
                                                for i, ph in enumerate(videos):
                                                    caption_text = name  + "\n" + text if i == 0 else None
                                                    media.append(InputMediaVideo(media=ph, caption=caption_text))
                                                tg_send_mes = await bot.send_media_group(chat_id=CHAT_ID, media=media) 
                                                await create_message_pair(mMAX_id=update['message']['body']['mid'], mTG_id=tg_send_mes[0].message_id, name=name)  
                                                logging.info(f"Сообщение VIDEO (без текста) tg: {tg_send_mes.message_id} MAX: {update['message']['body']['mid']} успешно отправлено!")

                                if files:                                           
                                                media = []
                                                name =  take_user_name(update['message']['sender']['user_id'], 'MAX') 
                                                if  name == False: 
                                                    name = 'Неизвестный пользователь'
                                                for i, ph in enumerate(files):
                                                    caption_text = name + "\n" + text if i == 0 else None
                                                    media.append(InputMediaDocument(media=ph , caption=caption_text))
                                                tg_send_mes = await bot.send_media_group(chat_id=CHAT_ID, media=media)
                                                create_message_pair(mMAX_id=update['message']['body']['mid'], mTG_id=tg_send_mes[0].message_id, name=name)   
                                                logging.info(f"Сообщение FILE (без текста) tg: {tg_send_mes.message_id} MAX: {update['message']['body']['mid']} успешно отправлено!")                                         






                        else:
                                if(update['update_type'] == 'message_created'):
                                    try:
                                        name = await take_user_name(update['message']['sender']['user_id'], 'MAX')
                                        if  name == False:
                                            name = 'Неизвестный пользователь'

                                        tg_send_mes = await bot.send_message(chat_id=CHAT_ID, text=name + "\n" + update['message']['body']['text'])
                                        await create_message_pair(mMAX_id=update['message']['body']['mid'], mTG_id=tg_send_mes.message_id, name=name)
                                        logging.info(f"Сообщение tg: {tg_send_mes.message_id} MAX: {update['message']['body']['mid']} успешно отправлено!")
                                    except Exception as e:
                                       logging.error(f"Ошибка при отправке ТЕКСТА: {e}")
                                    
                                # with open('logs.txt', mode='a', encoding="utf-8") as file:
                                #     file.write(str(data['updates'][i]['message']['recipient']['chat_id']) + "\n")
                                #     file.write(str(data['updates'][i]['message']['body']['text']) + "\n")
                                #     file.write(str(data['updates'][i]['message']['sender']) + "\n")
                        
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                # Обработка сетевых проблем или таймаута соединения
                print(f"Ошибка сети или таймаут: {e}. Повтор через {backoff_delay} сек.")
                await asyncio.sleep(backoff_delay)
                backoff_delay = min(backoff_delay * 2, 60)




# Запуск асинхронного скрипта
if __name__ == "__main__":
    try:
        asyncio.run(poll_api())
    except KeyboardInterrupt:
        print("\nПоллинг остановлен пользователем.")
