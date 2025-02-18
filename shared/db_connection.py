import os
import json
import psycopg
import asyncio

class DBConnection:
    def __init__(self):
        # Load sensitive data from local.settings.json
        with open('local.settings.json') as f:
            settings = json.load(f)
            self.connection_string = settings['Values']['DB_CONNECTION_STRING']

    async def execute_query(self, query):
        async with await psycopg.AsyncConnection.connect(self.connection_string) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query)
                return await cursor.fetchall()
