import asyncio
from templates import QuantumLauncher, Backend


class asyncQuantumLauncher(QuantumLauncher):

    def start(self, times: int = 1, real_backend: Backend = None, debugging=False) -> None:
        self.real_backend = self.backend if real_backend is None else real_backend
        self._async_running = 1
        self._results = []
        self.debugging: bool = debugging
        self._prepare_problem()
        asyncio.run(self.run_async(times))
        return self._results

    async def run_async_task(self, pool: asyncio.BaseEventLoop):
        if self.debugging:
            print('cloud task started')
        result = await pool.run_in_executor(None, self.algorithm.run, self.problem, self.backend)
        self._results.append(result)
        if self.debugging:
            print('cloud task finished')
        return result

    async def run_async_fake_task(self, pool: asyncio.BaseEventLoop):
        if self.debugging:
            print('local task started')
        result = await pool.run_in_executor(None, self.algorithm.run, self.problem, self.backend)
        self._results.append(result)
        if self.debugging:
            print('local task finished')
        return result

    async def run_async(self, times: int):
        if self.debugging:
            print('creating tasks started')
        pool = asyncio.get_event_loop()
        tasks = [self.run_async_task(pool) for _ in range(times)]
        tasks += [self.run_async_fake_task(pool)]
        await asyncio.gather(*tasks)
        if self.debugging:
            print('all tasks finished')
