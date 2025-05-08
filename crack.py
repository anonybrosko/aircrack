import asyncio
import subprocess
import pyrcrack
from rich.console import Console
from rich.prompt import Prompt

class Net:
    def __init__(self, interface):
        self.airmon = pyrcrack.AirmonNg()
        self.interface = interface
        self.networks = []

    async def scan_for_targets(self):
        """Scan for targets, return json."""
        console = Console()
        console.clear()
        console.show_cursor(False)

        async with self.airmon(self.interface) as mon:
            async with pyrcrack.AirodumpNg() as pdump:
                async for aps in pdump(mon.monitor_interface):
                    console.clear()
                    console.print(aps.table)
                    self.networks = aps
                    await asyncio.sleep(2)

    async def scan_target(self):
        console = Console()
        console.clear()
        console.show_cursor(False)
        count = 1
        network = []
        for i in self.networks:
            temp1 = i.asdict()
            temp2 = {'id': count}
            network.append({**temp2, **temp1})
            count += 1

        for i in network:
            if i['essid'] != '':
                print(f'{i["id"]} - {i["essid"]}')

        ans = Prompt.ask(
            'Select a network',
            choices = [str(i['id']) for i in network if i['essid'] != '']
        )
        ap = network[int(ans)-1]
        async with self.airmon(self.interface) as mon:
            async with pyrcrack.AirodumpNg() as pdump:
                async for result in pdump(mon.monitor_interface, **self.networks[int(ans)-1].airodump):
                    if self.networks[int(ans) - 1].clients is not None:
                        l = [a for a in self.networks[int(ans) - 1].clients]
                    console.clear()
                    console.print(result.table)
                    await asyncio.sleep(2)

subprocess.run('startM monitor', shell=True)
mynet = Net('wlp1s0')
try:
    asyncio.run(mynet.scan_for_targets())
except KeyboardInterrupt:
    try:
        asyncio.run(mynet.scan_target())
    except KeyboardInterrupt:
        subprocess.run('startM managed', shell=True)

