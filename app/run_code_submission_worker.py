import asyncio

from app.bootstrap.build_code_submission_worker import build_code_submission_worker


async def main() -> None:
    worker = build_code_submission_worker()
    await worker.run_forever()


if __name__ == '__main__':
    asyncio.run(main())