import io
import logging
from pathlib import Path
from typing import Dict

from ..services.download_service import PyTubeAdapter, StreamProtocol, YoutubeDownload, YTDLPAdapter
from ..utils.enums import AdapterType
from ..utils.exceptions import DownloadServiceError, InvalidPathError


_logger = logging.getLogger(__name__)


class DownloadServiceAdapter:

    DOWNLOAD_ADAPTER_TYPE = {
        AdapterType.PYTUBE: PyTubeAdapter,
        AdapterType.YTDLP: YTDLPAdapter,
    }

    def __init__(self, video_url: str, adapter_type: str, config: Dict[str, str]) -> None:
        self.video_url = video_url
        self.config = config
        self.adapter_type = self._check_adapter_type(adapter_type)

        self._downloader = YoutubeDownload()

    def to_buffer(self) -> bytes:
        buffer = io.BytesIO()
        adapter = self._get_download_adapter()
        return self._downloader.set_stream_to_buffer(adapter, buffer)

    def to_file(self, str_file_path: str) -> None:
        adapter = self._get_download_adapter()

        if not isinstance(str_file_path, str):
            _logger.error(f"Cannot save the file. The path is not valid: '{str_file_path}'.")
            raise InvalidPathError("File path does not exist. Must be set before saving.")

        file_path = Path(str_file_path)
        self._downloader.set_stream_to_file(adapter, file_path)

    def _get_download_adapter(self) -> StreamProtocol:
        download_adapter = self.DOWNLOAD_ADAPTER_TYPE.get(self.adapter_type)

        if not download_adapter:
            raise DownloadServiceError("Unsupported download adapter type")

        return download_adapter(self.video_url, self.config)

    @staticmethod
    def _check_adapter_type(adapter_type: str) -> AdapterType:
        if adapter_type not in (adapter.value for adapter in AdapterType):
            _logger.error(f"Cannot find the adapter type: '{adapter_type}'.")
            raise  DownloadServiceError(f"The adapter type '{adapter_type}' is not valid.")

        return AdapterType(adapter_type)
