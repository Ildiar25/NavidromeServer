from contextlib import contextmanager
from subprocess import CompletedProcess
from unittest.mock import MagicMock, patch
from typing import Iterator

from .base_mock_helper import BaseMock


class FFmpegMock(BaseMock):
    """
    Simulates different FFmpeg behaviours.

    Operations covered:
    -------------------
    - MP3 conversion

    For each operation, mocks are provided for:
    -------------------------------------------
    - Success case (return code 0)
    - Error case (return code 1)
    """

    SUBPROCESS_RUN_PATH = 'odoo.addons.music_manager.services.download_service.subprocess.run'

    @classmethod
    @contextmanager
    def success(cls) -> Iterator[MagicMock]:
        with patch(cls.SUBPROCESS_RUN_PATH) as mocked_subprocess_run:
            mocked_subprocess_run.return_value = cls.create_mock(
                CompletedProcess,
                returncode=0,
                stdout=b'Simulate MP3 conversion successful',
                stderr=b'',
            )

            yield mocked_subprocess_run

    @classmethod
    @contextmanager
    def error(cls, stderr_msg: str = 'SIMULATING ERROR || Simulate MP3 conversion error ||') -> Iterator[MagicMock]:
        with patch(cls.SUBPROCESS_RUN_PATH) as mocked_subprocess_run:
            mocked_subprocess_run.return_value = cls.create_mock(
                CompletedProcess,
                returncode=1,
                stdout=b'',
                stderr=stderr_msg.encode()
            )

            yield mocked_subprocess_run
