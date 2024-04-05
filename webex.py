import aiohttp
import asyncio
import logging

def _getToken():
    import json
    with open('config.json') as f:
        config = json.load(f)
    return config['botToken']

async def sendMessage(message):
    async with aiohttp.ClientSession() as session:
        token = _getToken()
        url = f"https://webexapis.com/v1/messages"
        headers = { 'Content-Type': 'application/json', 'Authorization': f'Bearer {token}' }

        async with session.post(url, headers=headers, json=message) as res:
            return await res.json()

async def searchForPerson(name):
    async with aiohttp.ClientSession() as session:
        token = _getToken()
        url = f"https://webexapis.com/v1/people/?displayName={name}"
        headers = { 'Content-Type': 'application/json', 'Authorization': f'Bearer {token}' }

        async with session.get(url, headers=headers) as res:
            result = await res.json()
            return result['items']

if __name__ == "__main__":
    recipient = 'someone@example.cisco.com'
    host = 'tore bjol'
    asyncio.run(searchForPerson(host))
    text = 'Test **msg** from Visitor registration bot'
    message = { 'email': recipient, 'markdown': text }
    asyncio.run(sendMessage(message))
