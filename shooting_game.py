import pygame
import random
import os
import math
import asyncio
import websockets
import json
from aiohttp import web

# 게임 상태를 저장할 클래스
class GameState:
    def __init__(self):
        self.player_x = 0
        self.player_y = 0
        self.player_health = 100
        self.score = 0
        self.bullets = []
        self.enemies = []
        self.powerups = []
        self.explosions = []
        self.game_over = False

    def to_dict(self):
        return {
            'player_x': self.player_x,
            'player_y': self.player_y,
            'player_health': self.player_health,
            'score': self.score,
            'bullets': [{'x': b.x, 'y': b.y} for b in self.bullets],
            'enemies': [{'x': e.x, 'y': e.y} for e in self.enemies],
            'powerups': [{'x': p.x, 'y': p.y, 'type': p.type} for p in self.powerups],
            'explosions': [{'x': ex.x, 'y': ex.y, 'radius': ex.radius} for ex in self.explosions],
            'game_over': self.game_over
        }

game_state = GameState()
connected_clients = set()

async def websocket_handler(websocket, path):
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            data = json.loads(message)
            if 'type' in data:
                if data['type'] == 'move':
                    game_state.player_x = data['x']
                    game_state.player_y = data['y']
                elif data['type'] == 'shoot':
                    # 총알 발사 로직
                    pass
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        connected_clients.remove(websocket)

async def broadcast_game_state():
    while True:
        if connected_clients:
            state_json = json.dumps(game_state.to_dict())
            await asyncio.gather(
                *[client.send(state_json) for client in connected_clients]
            )
        await asyncio.sleep(1/60)  # 60 FPS

async def game_loop():
    while True:
        # 게임 로직 업데이트
        # 적 생성, 총알 이동, 충돌 검사 등
        await asyncio.sleep(1/60)

async def init_app():
    app = web.Application()
    app.router.add_static('/', path=os.path.dirname(__file__))
    return app

async def main():
    app = await init_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()
    
    ws_server = await websockets.serve(websocket_handler, 'localhost', 8081)
    
    await asyncio.gather(
        game_loop(),
        broadcast_game_state()
    )

if __name__ == '__main__':
    asyncio.run(main()) 