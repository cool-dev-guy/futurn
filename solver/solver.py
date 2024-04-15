import random
import asyncio
from functools import lru_cache

class Solver:
    def __init__(self, playwright, proxy="", headless=True):
        self.playwright = playwright
        self.proxy:str = proxy
        self.headless:bool = headless

        self.browser = None

    async def start_browser(self):
        if self.proxy:
            self.browser = await self.playwright.firefox.launch(headless=self.headless, proxy={
                "server": "http://" + self.proxy.split("@")[1],
                "username": self.proxy.split("@")[0].split(":")[0],
                "password": self.proxy.split("@")[0].split(":")[1]
            })
        else:
            self.browser = await self.playwright.firefox.launch(
                headless=self.headless,
                devtools=False,
#                args=["--no-sandbox"],
            )

    async def terminate(self):
        if self.browser:
            await self.browser.close()

    @lru_cache(maxsize=None)
    async def build_page_data(self):
        self.html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>body's solver</title>
            <script src="https://challenges.cloudflare.com/turnstile/v0/api.js?onload=onloadTurnstileCallback" async defer></script>
        </head>
        <body>
            <span>solver available at https://github.com/Body-Alhoha/turnaround</span>
            <div class="cf-turnstile" data-sitekey="{self.sitekey}"></div>
        </body>
        </html>
        """

    def get_mouse_path(self, x1:int, y1:int, x2:int, y2:int)->list:
        path:list = []
        x, y = x1, y1
        while abs(x - x2) > 3 or abs(y - y2) > 3:
            diff:int = abs(x - x2) + abs(y - y2)
            speed:int = random.randint(1, 2)
            if diff < 20:
                speed = random.randint(1, 3)
            else:
                speed *= diff / 45

            if abs(x - x2) > 3:
                x += speed * ((x2 - x) / abs(x2 - x))
            if abs(y - y2) > 3:
                y += speed * ((y2 - y) / abs(y2 - y))
            path.append((x, y))
        return path

    async def move_to(self, x:int, y:int):
        for path in self.get_mouse_path(self.current_x, self.current_y, x, y):
            await self.page.mouse.move(path[0], path[1])
            if random.randint(0, 100) > 15:
                await asyncio.sleep(1 / random.randint(900, 1000))

    async def solve_invisible(self):
        iterations:int = 0
        while iterations < 10:
            self.random_x:int = random.randint(0, self.window_width)
            self.random_y:int = random.randint(0, self.window_height)
            iterations += 1

            await self.move_to(self.random_x, self.random_y)
            self.current_x:int = self.random_x
            self.current_y:int = self.random_y

            elem = await self.page.query_selector("[name=cf-turnstile-response]")
            attrib = await elem.get_attribute("value");
            if elem and attrib:
                return attrib

            await asyncio.sleep(1 / random.randint(900, 1000))
        return "failed"

    async def solve_visible(self):
        return "failed"
        iframe = await self.page.query_selector("iframe")
        while not iframe:
            iframe = await self.page.query_selector("iframe")
            await asyncio.sleep(0.1)
        while not await iframe.bounding_box():
            await asyncio.sleep(0.1)
        bbox = await iframe.bounding_box()
        x:int = bbox["x"] + random.randint(5, 12)
        y:int = bbox["y"] + random.randint(5, 12)
        await self.move_to(x, y)
        self.current_x:int = x
        self.current_y:int = y
        framepage = await iframe.content_frame()
        checkbox = await framepage.query_selector("input")

        while not checkbox:
            checkbox = await framepage.query_selector("input")
            await asyncio.sleep(0.1)

        cbbox = await checkbox.bounding_box()
        width = cbbox["width"]
        height = cbbox["height"]
        
        x = cbbox["x"] + width / 5 + random.randint(int(width / 5), int(width - width / 5))
        y = cbbox["y"] + height / 5 + random.randint(int(height / 5), int(height - height / 5))

        await self.move_to(x, y)

        self.current_x = x
        self.current_y = y
        

        await asyncio.sleep(random.randint(1, 5) / random.randint(400, 600))
        await self.page.mouse.click(x, y)

        iterations:int = 0

        while iterations < 10:
            self.random_x = random.randint(0, self.window_width)
            self.random_y = random.randint(0, self.window_height)
            iterations += 1

            await self.move_to(self.random_x, self.random_y)
            self.current_x = self.random_x
            self.current_y = self.random_y
            elem = await self.page.query_selector("[name=cf-turnstile-response]")
            attrib = await elem.get_attribute("value");
            if elem and attrib:
                return attrib
            await asyncio.sleep(random.randint(2, 5) / random.randint(400, 600))
        return "failed"
    async def solve(self, url:str, sitekey:str, invisible:bool=False):
        self.url:str = url + "/" if not url.endswith("/") else url
        self.sitekey:str = sitekey
        await self.start_browser()
        self.context = await self.browser.new_context(
            viewport={'width': 50, 'height': 50},
            ignore_https_errors=True,
            device_scale_factor=1
            )
        self.page = await self.context.new_page()

        await self.build_page_data()

        await self.page.route(self.url, lambda route: route.fulfill(body=self.html, status=200))
        await self.page.goto(self.url)
        output:str = "failed"
        self.current_x:int = 0
        self.current_y:int = 0
        self.window_width:int = 50
        self.window_height:int = 50

        if invisible:
            output = await self.solve_invisible()
        else:
            output = await self.solve_visible()

        await self.terminate()
        return output
