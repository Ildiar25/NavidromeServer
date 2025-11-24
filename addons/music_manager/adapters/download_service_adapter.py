import io
import logging

from ..services.download_service import PyTubeAdapter, StreamProtocol, YoutubeDownload, YTDLPAdapter
from ..utils.enums import AdapterType
from ..utils.exceptions import DownloadServiceError


_logger = logging.getLogger(__name__)


class DownloadServiceAdapter:

    def __init__(self, video_url: str, adaper_type: AdapterType = AdapterType.YTDLP) -> None:
        self.video_url = video_url
        self.adapter_type = adaper_type
        self._downloader = YoutubeDownload()

    def to_buffer(self) -> bytes:
        buffer = io.BytesIO()
        adapter = self._get_download_adapter()
        return self._downloader.set_stream_to_buffer(adapter, buffer)

    def to_file(self, filepath:str) -> None:
        adapter = self._get_download_adapter()
        self._downloader.set_stream_to_file(adapter, filepath)

    def _get_download_adapter(self) -> StreamProtocol:
        match self.adapter_type:
            case AdapterType.PYTUBE:
                return PyTubeAdapter(self.video_url)

            case AdapterType.YTDLP:
                return YTDLPAdapter(self.video_url)

            case _:
                raise DownloadServiceError("Unsupported download adapter type")
