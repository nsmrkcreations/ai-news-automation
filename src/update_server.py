from aiohttp import web
import asyncio
import json
from core.real_time_aggregator import RealTimeNewsAggregator
from core.logger import setup_logger
import os

logger = setup_logger()

class NewsUpdateServer:
    def __init__(self):
        self.app = web.Application()
        self.setup_routes()
        self.connected_clients = set()
        self.aggregator = RealTimeNewsAggregator(
            api_key=os.getenv('NEWS_API_KEY'),
            update_callback=self.broadcast_updates
        )
    
    def setup_routes(self):
        self.app.router.add_get('/news-updates', self.websocket_handler)
        self.app.router.add_get('/api/news', self.get_news)
        
    async def start(self):
        """Start the server and news aggregator"""
        # Start news aggregator in background
        asyncio.create_task(self.aggregator.start_real_time_updates())
        
        # Start web server
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', 8080)
        await site.start()
        logger.info("News update server started on http://localhost:8080")
    
    async def websocket_handler(self, request):
        """Handle WebSocket connections"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        # Get user preferences from query parameters
        preferences = {
            'categories': request.query.get('categories', 'all').split(','),
            'breakingNews': request.query.get('breaking', 'true').lower() == 'true',
            'minScore': float(request.query.get('minScore', '0')),
            'updateFrequency': request.query.get('frequency', 'standard')
        }
        
        # Add client with their preferences
        client_info = {
            'ws': ws,
            'preferences': preferences,
            'last_update': datetime.utcnow()
        }
        self.connected_clients.add(client_info)
        logger.info(f"New client connected with preferences: {preferences}")
        
        try:
            # Send initial news data
            with open('public/data/news.json', 'r', encoding='utf-8') as f:
                initial_data = json.load(f)
                await ws.send_json({
                    'type': 'initial',
                    'articles': initial_data
                })
            
            # Handle client messages
            async for msg in ws:
                if msg.type == web.WSMsgType.ERROR:
                    logger.error(f"WebSocket error: {ws.exception()}")
        
        finally:
            # Remove client when disconnected
            self.connected_clients.remove(ws)
            logger.info(f"Client disconnected. Remaining clients: {len(self.connected_clients)}")
        
        return ws
    
    async def get_news(self, request):
        """REST API endpoint for getting news"""
        try:
            with open('public/data/news.json', 'r', encoding='utf-8') as f:
                news_data = json.load(f)
            
            # Handle category filter
            category = request.query.get('category')
            if category and category != 'all':
                news_data = [article for article in news_data if article['category'] == category]
            
            return web.json_response(news_data)
            
        except Exception as e:
            logger.error(f"Error serving news data: {e}")
            return web.Response(status=500)
    
    async def broadcast_updates(self, new_articles):
        """Broadcast updates to all connected clients based on their preferences"""
        if not self.connected_clients or not new_articles:
            return
            
        dead_clients = set()
        current_time = datetime.utcnow()
        
        for client_info in self.connected_clients:
            try:
                ws = client_info['ws']
                prefs = client_info['preferences']
                
                # Filter articles based on client preferences
                filtered_articles = self.filter_articles_for_client(
                    new_articles, 
                    prefs,
                    client_info['last_update']
                )
                
                if filtered_articles:
                    # Separate breaking and regular news
                    breaking_news = [a for a in filtered_articles if a.get('isBreaking')]
                    regular_news = [a for a in filtered_articles if not a.get('isBreaking')]
                    
                    # Send breaking news immediately
                    if breaking_news and prefs['breakingNews']:
                        await ws.send_json({
                            'type': 'breaking',
                            'articles': breaking_news
                        })
                    
                    # Send regular updates based on frequency preference
                    if regular_news:
                        update_due = self.check_update_timing(
                            client_info['last_update'],
                            prefs['updateFrequency']
                        )
                        
                        if update_due:
                            await ws.send_json({
                                'type': 'update',
                                'articles': regular_news
                            })
                            client_info['last_update'] = current_time
                
            except Exception as e:
                logger.error(f"Error sending update to client: {e}")
                dead_clients.add(client_info)
        
        # Remove dead clients
        self.connected_clients -= dead_clients
        
    def filter_articles_for_client(self, articles, preferences, last_update):
        """Filter articles based on client preferences"""
        filtered = []
        categories = preferences['categories']
        min_score = preferences['minScore']
        
        for article in articles:
            # Check category preference
            if categories != ['all'] and article['category'] not in categories:
                continue
                
            # Check importance score
            if article.get('importanceScore', 0) < min_score:
                continue
                
            filtered.append(article)
            
        return filtered
        
    def check_update_timing(self, last_update, frequency):
        """Check if it's time to send an update based on frequency preference"""
        if frequency == 'realtime':
            return True
            
        elapsed = (datetime.utcnow() - last_update).total_seconds()
        
        if frequency == 'standard':
            return elapsed >= 300  # 5 minutes
        elif frequency == 'digest':
            return elapsed >= 3600  # 1 hour
        else:
            return True  # Default to realtime for unknown frequencies

async def start_server():
    server = NewsUpdateServer()
    await server.start()
    
    # Keep server running
    while True:
        await asyncio.sleep(3600)  # Check every hour

if __name__ == "__main__":
    asyncio.run(start_server())
