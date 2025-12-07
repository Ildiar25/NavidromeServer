from subprocess import CompletedProcess
from typing import ContextManager
from unittest.mock import MagicMock, patch

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
    def success(cls) -> ContextManager[MagicMock]:
        mock_subprocess = cls._subprocess_mock_helper("Successful MP3 convertion...")
        return patch(cls.SUBPROCESS_RUN_PATH, return_value=mock_subprocess)

    @classmethod
    def error(cls) -> ContextManager[MagicMock]:
        mock_subprocess = cls._subprocess_mock_helper("Failed MP3 convertion...", with_error=True)
        return patch(cls.SUBPROCESS_RUN_PATH, return_value=mock_subprocess)

    @classmethod
    def _subprocess_mock_helper(cls, message: str, with_error: bool = False) -> MagicMock:
        mock_completed_process = cls.create_mock(CompletedProcess)

        options = {
            'returncode': 1 if with_error else 0,
            'stdout': b'' if with_error else message.encode(),
            'stderr': message.encode() if with_error else b'',
        }

        if with_error:
            for key, value in options.items():
                setattr(mock_completed_process, key, value)

        else:
            for key, value in options.items():
                setattr(mock_completed_process, key, value)

        return mock_completed_process
