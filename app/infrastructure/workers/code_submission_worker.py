import logging

from app.application.exceptions import RetryableExecutionError
from app.application.interfaces.submission_queue import SubmissionQueue
from app.application.use_cases.code_submissions.process_code_submission import (
    ProcessCodeSubmissionCommand,
    ProcessCodeSubmissionUseCase,
)

logger = logging.getLogger(__name__)


class CodeSubmissionWorker:
    def __init__(
        self,
        queue: SubmissionQueue,
        process_use_case: ProcessCodeSubmissionUseCase,
    ) -> None:
        self.queue = queue
        self.process_use_case = process_use_case

    async def run_once(self) -> None:
        try:
            submission_id = await self.queue.dequeue()
        except Exception:
            logger.exception('Code submission queue dequeue failed')
            return

        try:
            await self.process_use_case.execute(
                ProcessCodeSubmissionCommand(submission_id=submission_id)
            )
        except RetryableExecutionError:
            logger.warning(
                'Code submission processing will be retried',
                extra={'submission_id': str(submission_id)},
            )
            await self.queue.enqueue(submission_id)
        except Exception:
            logger.exception(
                'Code submission processing failed',
                extra={'submission_id': str(submission_id)},
            )

    async def run_forever(self) -> None:
        while True:
            await self.run_once()
